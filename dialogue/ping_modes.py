# ==========================================
# Файл: dialogue/ping_modes.py
# Справка: README.md → Настройки пинга
# Задача: применять интервал пинга из config.json
# Комментарий: вызывается при изменении настроек пинга в админке
# Зависит от: json, ping_utils
# Вызывается из: admin_commands.py (при изменении интервала)
# ==========================================

import os
import json
from ping_utils import start_background_pinger

# Путь к файлу конфигурации
CONFIG_FILE = os.path.join('dialogue', 'data', 'config.json')

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def apply_ping_mode():
    config = load_config()
    interval = config.get("ping", {}).get("interval", 60)
    start_background_pinger(interval)
    print(f"Пингер установлен на {interval} секунд")
