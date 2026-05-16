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
    
    # Проверяем принудительный режим (force_mode)
    force_mode = config.get("force_mode")
    force_until_str = config.get("force_mode_until")
    
    if force_mode and force_until_str:
        try:
            force_until = datetime.strptime(force_until_str, "%Y-%m-%d %H:%M:%S")
            if datetime.now() < force_until:
                return force_mode
            else:
                # Принудительный режим истёк — удаляем
                config.pop("force_mode", None)
                config.pop("force_mode_until", None)
                save_config(config)
        except:
            pass
    
    # Если принудительного режима нет — используем расписание по часам
    now = datetime.now()
    hour = now.hour
    schedule = config.get("schedule", {
        "утро": {"hour_start": 6, "hour_end": 12},
        "день": {"hour_start": 12, "hour_end": 20},
        "вечер": {"hour_start": 20, "hour_end": 23},
        "сон": {"hour_start": 23, "hour_end": 6}
    })
    
    for mode, times in schedule.items():
        start = times["hour_start"]
        end = times["hour_end"]
        # Обрабатываем переход через полночь (например, сон 23 → 6)
        if start <= hour < end or (start > end and (hour >= start or hour < end)):
            return mode
    
    return "сон"  # fallback

def should_respond_to_talk():
    mode = get_current_activity_mode()
    # В режиме "сон" не отвечаем на #говорим
    return mode != "сон"

def should_publish_quotes():
    mode = get_current_activity_mode()
    # Цитаты публикуем только в "утро" и "день"
    return mode in ["утро", "день"]

def get_ping_interval_for_mode(mode=None):
    if mode is None:
        mode = get_current_activity_mode()
    config = load_config()
    schedule = config.get("schedule", {})
    if mode in schedule:
        return schedule[mode].get("ping_interval", 60)
    return 60
