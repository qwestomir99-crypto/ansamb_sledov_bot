# ==========================================
# Модуль: dialogue/adaptive_modes.py
# Справка: README.md → Адаптивные режимы
# Задача: динамическое изменение режимов на основе метрик
# Комментарий: работает поверх эталонных режимов, возвращается к ним при тупике
# Зависит от: config.json, settings.py
# Вызывается из: activity_modes.py
# ==========================================

import os
import json
import time
from datetime import datetime, timedelta
from collections import deque

CONFIG_FILE = "config.json"
ADAPTIVE_STATE_FILE = "dialogue/data/adaptive_state.json"

# Настройки адаптации (могут быть переопределены в settings.py)
ADAPTIVE_ENABLED = True
ADAPTIVE_COOLDOWN = 3600  # 1 час между сменами режимов
DEADEND_TIMEOUT = 7200    # 2 часа тупика → возврат к эталону

# История метрик
metrics_history = deque(maxlen=100)

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def load_adaptive_state():
    """Загружает состояние адаптации с защитой от пустого/битого файла"""
    if not os.path.exists(ADAPTIVE_STATE_FILE):
        return {
            "last_switch": 0,
            "current_adaptive_mode": None,
            "deadend_count": 0,
            "last_return_to_etalon": 0
        }
    try:
        with open(ADAPTIVE_STATE_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                print("[ADAPTIVE] Файл состояния пуст, создаём новый")
                return {
                    "last_switch": 0,
                    "current_adaptive_mode": None,
                    "deadend_count": 0,
                    "last_return_to_etalon": 0
                }
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"[ADAPTIVE] Ошибка парсинга состояния: {e}, создаём новый файл")
        return {
            "last_switch": 0,
            "current_adaptive_mode": None,
            "deadend_count": 0,
            "last_return_to_etalon": 0
        }
    except Exception as e:
        print(f"[ADAPTIVE] Ошибка чтения состояния: {e}")
        return {
            "last_switch": 0,
            "current_adaptive_mode": None,
            "deadend_count": 0,
            "last_return_to_etalon": 0
        }

def save_adaptive_state(state):
    os.makedirs(os.path.dirname(ADAPTIVE_STATE_FILE), exist_ok=True)
    with open(ADAPTIVE_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def collect_metrics():
    """Собирает метрики для адаптации"""
    metrics = {
        "errors_last_hour": count_errors_last_hour(),
        "commands_last_hour": count_commands_last_hour(),
        "vk_views_last_hour": get_vk_views_last_hour(),
        "is_weekend": datetime.now().weekday() >= 5,
        "hour": datetime.now().hour,
        "last_publication_age": get_last_publication_age()
    }
    metrics_history.append({**metrics, "timestamp": time.time()})
    return metrics

def count_errors_last_hour():
    """Считает ошибки в error.log за последний час"""
    if not os.path.exists("error.log"):
        return 0
    try:
        one_hour_ago = time.time() - 3600
        with open("error.log", "r") as f:
            lines = f.readlines()
        return len(lines)
    except:
        return 0

def count_commands_last_hour():
    """Считает команды #говори и #меню за последний час"""
    if not os.path.exists("admin.log"):
        return 0
    try:
        with open("admin.log", "r") as f:
            lines = f.readlines()
        commands = 0
        for line in lines:
            if "#говори" in line or "#меню" in line:
                commands += 1
        return commands
    except:
        return 0

def get_vk_views_last_hour():
    """Получает просмотры из VK"""
    return 0

def get_last_publication_age():
    """Возраст последней публикации в минутах"""
    pubs_file = "publications.json"
    if not os.path.exists(pubs_file):
        return 999
    try:
        with open(pubs_file, "r") as f:
            pubs = json.load(f)
        if not pubs:
            return 999
        last_pub = max(pubs, key=lambda x: x.get("publish_at", 0))
        age = (time.time() - last_pub.get("publish_at", 0)) / 60
        return int(age)
    except:
        return 999

def get_adaptive_mode(metrics):
    """
    Определяет адаптивный режим на основе метрик
    Возвращает: "ускоренный", "замедленный", "ночной", "авральный", "сон"
    """
    errors = metrics.get("errors_last_hour", 0)
    commands = metrics.get("commands_last_hour", 0)
    is_weekend = metrics.get("is_weekend", False)
    hour = metrics.get("hour", 0)
    last_pub_age = metrics.get("last_publication_age", 999)
    
    if errors > 10:
        return "авральный"
    
    if hour < 6 or hour > 23:
        if commands < 3 and last_pub_age > 120:
            return "ночной"
    
    if commands > 20 or (is_weekend and commands > 10):
        return "ускоренный"
    
    if commands < 3 and last_pub_age > 60:
        return "замедленный"
    
    if commands == 0 and last_pub_age > 180:
        return "сон"
    
    return "обычный"

def is_dead_end(adaptive_mode, metrics):
    """Проверяет, зашёл ли адаптивный режим в тупик"""
    errors = metrics.get("errors_last_hour", 0)
    commands = metrics.get("commands_last_hour", 0)
    last_pub_age = metrics.get("last_publication_age", 999)
    
    if errors > 15:
        return True
    
    if commands == 0 and last_pub_age > 180:
        return True
    
    if last_pub_age > 240:
        return True
    
    return False

def get_etalon_mode_by_time():
    """Возвращает эталонный режим по времени"""
    config = load_config()
    current_hour = datetime.now().hour
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
    return "день"

def get_adaptive_interval(base_interval, adaptive_mode):
    """Корректирует интервал в зависимости от адаптивного режима"""
    if adaptive_mode == "ускоренный":
        return max(15, base_interval // 2)
    elif adaptive_mode == "замедленный":
        return min(480, base_interval * 2)
    elif adaptive_mode == "авральный":
        return 0
    elif adaptive_mode == "сон":
        return 0
    else:
        return base_interval

def get_current_adaptive_mode():
    """
    Главная функция: возвращает текущий режим (адаптивный или эталонный)
    """
    global ADAPTIVE_ENABLED
    try:
        from settings import ADAPTIVE_ENABLED as SETTINGS_ADAPTIVE
        ADAPTIVE_ENABLED = SETTINGS_ADAPTIVE
    except:
        pass
    
    if not ADAPTIVE_ENABLED:
        return get_etalon_mode_by_time()
    
    state = load_adaptive_state()
    metrics = collect_metrics()
    adaptive_mode = get_adaptive_mode(metrics)
    
    if is_dead_end(adaptive_mode, metrics):
        print(f"[ADAPTIVE] Тупик в режиме {adaptive_mode}, возврат к эталону")
        state["last_return_to_etalon"] = time.time()
        state["deadend_count"] += 1
        save_adaptive_state(state)
        return get_etalon_mode_by_time()
    
    now = time.time()
    if adaptive_mode != state.get("current_adaptive_mode"):
        if now - state.get("last_switch", 0) > ADAPTIVE_COOLDOWN:
            print(f"[ADAPTIVE] Смена режима: {state.get('current_adaptive_mode')} → {adaptive_mode}")
            state["last_switch"] = now
            state["current_adaptive_mode"] = adaptive_mode
            save_adaptive_state(state)
        else:
            adaptive_mode = state.get("current_adaptive_mode", "обычный")
    
    return adaptive_mode

def get_adaptive_quotes_interval(base_interval):
    """Возвращает скорректированный интервал цитат"""
    adaptive_mode = get_current_adaptive_mode()
    return get_adaptive_interval(base_interval, adaptive_mode)

def get_adaptive_publisher_interval(base_interval):
    """Возвращает скорректированный интервал публикаций"""
    adaptive_mode = get_current_adaptive_mode()
    return get_adaptive_interval(base_interval, adaptive_mode)

def should_adaptive_publish():
    """Проверяет, нужно ли публиковать в адаптивном режиме"""
    adaptive_mode = get_current_adaptive_mode()
    if adaptive_mode in ["авральный", "сон"]:
        return False
    return True

def reset_to_etalon():
    """Принудительный сброс к эталонным режимам"""
    state = load_adaptive_state()
    state["current_adaptive_mode"] = None
    state["deadend_count"] = 0
    state["last_return_to_etalon"] = time.time()
    save_adaptive_state(state)
    print("[ADAPTIVE] Принудительный сброс к эталонным режимам")
    return True
