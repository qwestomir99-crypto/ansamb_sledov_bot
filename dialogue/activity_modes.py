import json
from datetime import datetime
from dialogue.ping_modes import apply_ping_mode
from dialogue.activity_modes import get_current_activity_mode

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_current_activity_mode():
    now = datetime.now()
    hour = now.hour
    config = load_config()
    schedule = config.get("schedule", {})
    for mode, times in schedule.items():
        start = times["hour_start"]
        end = times["hour_end"]
        if start <= hour < end or (start > end and (hour >= start or hour < end)):
            return mode
    return "сон"

def should_respond_to_talk():
    mode = get_current_activity_mode()
    # В режиме "сон" не отвечаем на #говорим
    return mode != "сон"

def should_publish_quotes():
    mode = get_current_activity_mode()
    # Цитаты публикуем только в "утро" и "день"
    return mode in ["утро", "день"]
