# ==========================================
# Модуль: dialogue/activity_modes.py
# Справка: README.md → Режимы дня
# Задача: определение текущего режима (эталонного или адаптивного)
# Комментарий: поддерживает адаптивные режимы и Шаббат
# Зависит от: config.json, settings.py, adaptive_modes.py, shabbat_manager.py
# Вызывается из: bot.py, publisher.py, quotes.py
# ==========================================

import json
from datetime import datetime
from debug_utils import debug_log
from dialogue.shabbat_manager import is_shabbat

CONFIG_FILE = "config.json"

# Импорт адаптивных режимов (если модуль есть)
try:
    from dialogue.adaptive_modes import (
        get_current_adaptive_mode,
        get_adaptive_quotes_interval,
        get_adaptive_publisher_interval,
        should_adaptive_publish,
        ADAPTIVE_ENABLED
    )
    ADAPTIVE_AVAILABLE = True
    print("[ACTIVITY_MODES] Адаптивные режимы загружены")
except ImportError:
    ADAPTIVE_AVAILABLE = False
    print("[ACTIVITY_MODES] Адаптивные режимы не доступны, использую эталон")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_current_mode():
    """Возвращает текущий режим (адаптивный или эталонный)"""
    if ADAPTIVE_AVAILABLE and ADAPTIVE_ENABLED:
        adaptive_mode = get_current_adaptive_mode()
        if adaptive_mode and adaptive_mode != "обычный":
            return adaptive_mode
    
    # Иначе — эталонный режим по времени
    config = load_config()
    force_mode = config.get("force_mode")
    force_mode_until = config.get("force_mode_until")
    
    if force_mode and force_mode_until:
        until = datetime.strptime(force_mode_until, "%Y-%m-%d %H:%M:%S")
        if datetime.now() < until:
            return force_mode
    
    now = datetime.now()
    current_hour = now.hour
    
    modes = config.get("modes", {})
    
    for mode_name, mode_config in modes.items():
        start = mode_config.get("hour_start")
        end = mode_config.get("hour_end")
        
        if start <= end:
            if start <= current_hour < end:
                return mode_name
        else:
            if current_hour >= start or current_hour < end:
                return mode_name
    
    return "день"  # fallback

def get_current_activity_mode():
    """Совместимость со старым scheduler.py"""
    return get_current_mode()

def get_current_mode_config():
    """Возвращает конфиг текущего режима (с учётом адаптации и Шаббата)"""
    
    # === ШАББАТ ===
    if is_shabbat():
        debug_log("ACTIVITY_MODES", "Шаббат — режим покоя")
        return {
            "quotes_interval": 0,
            "publisher_interval": 0,
            "publisher": False,
            "quotes": False,
            "talk": False,
            "ping_interval": 300
        }
    # ===============
    
    mode = get_current_mode()
    config = load_config()
    modes = config.get("modes", {})
    
    # Получаем базовый конфиг режима
    if mode in modes:
        mode_config = modes[mode].copy()
    else:
        mode_config = {}
    
    # Если адаптивные режимы включены, корректируем интервалы
    if ADAPTIVE_AVAILABLE and ADAPTIVE_ENABLED:
        base_quotes_interval = mode_config.get("quotes_interval", 60)
        base_publisher_interval = mode_config.get("publisher_interval", 0)
        
        mode_config["quotes_interval"] = get_adaptive_quotes_interval(base_quotes_interval)
        mode_config["publisher_interval"] = get_adaptive_publisher_interval(base_publisher_interval)
        mode_config["publisher"] = should_adaptive_publish()
    
    return mode_config

def should_respond_to_talk():
    """Можно ли отвечать на #говори"""
    mode_config = get_current_mode_config()
    return mode_config.get("talk", True)

def should_publish_quotes():
    """Можно ли публиковать цитаты"""
    mode_config = get_current_mode_config()
    return mode_config.get("quotes", True)

def should_publish():
    """Можно ли публиковать отложенные посты"""
    mode_config = get_current_mode_config()
    return mode_config.get("publisher", True)

def get_quotes_interval():
    """Возвращает интервал цитат в минутах для текущего режима"""
    mode_config = get_current_mode_config()
    return mode_config.get("quotes_interval", 60)

def get_ping_interval():
    """Возвращает интервал пинга в секундах для текущего режима"""
    mode_config = get_current_mode_config()
    return mode_config.get("ping_interval", 60)

def get_publisher_interval():
    """Возвращает интервал публикаций в минутах для текущего режима"""
    mode_config = get_current_mode_config()
    return mode_config.get("publisher_interval", 0)

# ==========================================
# ДОБАВЛЕНА ФУНКЦИЯ ДЛЯ СОВМЕСТИМОСТИ С modes.py
# ==========================================
def set_mode(mode_name):
    """Устанавливает принудительный режим (для админки)"""
    config = load_config()
    config["force_mode"] = mode_name
    config["force_mode_until"] = (datetime.now().replace(hour=23, minute=59, second=59)).strftime("%Y-%m-%d %H:%M:%S")
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    debug_log("ACTIVITY_MODES", f"Принудительно установлен режим: {mode_name}")
