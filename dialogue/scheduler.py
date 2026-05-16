import time
import threading
import json
from datetime import datetime
from ping_modes import apply_ping_mode
from activity_modes import get_current_activity_mode

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def update_ping_from_schedule():
    config = load_config()
    mode = get_current_activity_mode()
    schedule = config.get("schedule", {})
    if mode in schedule:
        new_interval = schedule[mode]["ping_interval"]
        if config.get("ping_interval") != new_interval:
            config["ping_interval"] = new_interval
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
            apply_ping_mode()
            print(f"[Scheduler] Переключен режим {mode}, пинг {new_interval} сек")

def scheduler_loop():
    while True:
        now = datetime.now()
        # Следующая проверка через минуту, но в момент смены часа (00, 06, 12, 18)
        next_check = 60
        if now.minute == 0 and now.second == 0:
            update_ping_from_schedule()
            next_check = 60
        time.sleep(next_check)
