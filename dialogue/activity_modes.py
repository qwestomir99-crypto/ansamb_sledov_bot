import json
from datetime import datetime

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get_current_activity_mode():
    config = load_config()
    if config is None:
        return "утро"
    
    # Проверяем принудительный режим
    force_mode = config.get("force_mode")
    force_until_str = config.get("force_mode_until")
    
    if force_mode and force_until_str:
        try:
            force_until = datetime.strptime(force_until_str, "%Y-%m-%d %H:%M:%S")
            if datetime.now() < force_until:
                return force_mode
            else:
                config.pop("force_mode", None)
                config.pop("force_mode_until", None)
                save_config(config)
        except:
            pass
    
    # Определяем режим по часам
    now = datetime.now()
    hour = now.hour
    modes = config.get("modes", {})
    
    for mode, times in modes.items():
        start = times.get("hour_start", 0)
        end = times.get("hour_end", 24)
        if start <= hour < end or (start > end and (hour >= start or hour < end)):
            return mode
    
    return "сон"

def should_respond_to_talk():
    mode = get_current_activity_mode()
    config = load_config()
    modes = config.get("modes", {})
    return modes.get(mode, {}).get("talk", True)

def should_publish_quotes():
    mode = get_current_activity_mode()
    config = load_config()
    modes = config.get("modes", {})
    return modes.get(mode, {}).get("quotes", False)

def get_ping_interval_for_mode(mode=None):
    if mode is None:
        mode = get_current_activity_mode()
    config = load_config()
    modes = config.get("modes", {})
    return modes.get(mode, {}).get("ping_interval", 60)
