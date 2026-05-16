import json
from datetime import datetime

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_current_mode():
    """Определяет текущий режим по времени или force_mode"""
    config = load_config()
    
    # Проверяем принудительный режим
    force_mode = config.get("force_mode")
    force_mode_until = config.get("force_mode_until")
    
    if force_mode and force_mode_until:
        until = datetime.strptime(force_mode_until, "%Y-%m-%d %H:%M:%S")
        if datetime.now() < until:
            return force_mode
    
    # Определяем по времени
    now = datetime.now()
    current_hour = now.hour
    
    modes = config.get("modes", {})
    
    for mode_name, mode_config in modes.items():
        start = mode_config.get("hour_start")
        end = mode_config.get("hour_end")
        
        if start <= end:
            if start <= current_hour < end:
                return mode_name
        else:  # через полночь (например, 23:00 - 06:00)
            if current_hour >= start or current_hour < end:
                return mode_name
    
    return "день"  # fallback

def get_current_activity_mode():
    """Совместимость со старым scheduler.py"""
    return get_current_mode()

def get_current_mode_config():
    """Возвращает конфиг текущего режима"""
    mode = get_current_mode()
    config = load_config()
    modes = config.get("modes", {})
    return modes.get(mode, {})

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
