import threading
import time
import json
from ping_utils import start_background_pinger

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def apply_ping_mode():
    config = load_config()
    interval = config.get("ping_interval", 60)
    # Перезапускаем пингер с новым интервалом
    start_background_pinger(interval)
    print(f"Пингер установлен на {interval} секунд")
