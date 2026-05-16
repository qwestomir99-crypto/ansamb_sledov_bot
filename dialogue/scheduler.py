import time
import threading
import json
from datetime import datetime
from dialogue.ping_modes import apply_ping_mode
from dialogue.activity_modes import get_current_activity_mode

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def update_ping_from_schedule():
    config = load_config()
    mode = get_current_activity_mode()
    modes = config.get("modes", {})
    if mode in modes:
        new_interval = modes[mode].get("ping_interval", 60)
        if config.get("ping", {}).get("interval") != new_interval:
            if "ping" not in config:
                config["ping"] = {}
            config["ping"]["interval"] = new_interval
            save_config(config)
            apply_ping_mode()
            print(f"[Scheduler] Переключен режим {mode}, пинг {new_interval} сек")

def scheduler_loop():
    while True:
        now = datetime.now()
        # Проверяем в начале каждого часа
        if now.minute == 0 and now.second == 0:
            update_ping_from_schedule()
        time.sleep(60)
