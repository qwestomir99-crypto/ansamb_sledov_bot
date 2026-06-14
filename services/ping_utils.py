# ==========================================
# Файл: services/ping_utils.py
# Справка: README.md → Пингер
# Задача: фоновый пинг бота, чтобы он не засыпал
# ==========================================

import time
import json
import os
import threading
import requests

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================

CONFIG_FILE = "config.json"

def load_config():
    """Загружает конфиг с защитой от байтов"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print(f"[PING] config.json не найден, использую значения по умолчанию")
            return {}
    except Exception as e:
        print(f"[PING] Ошибка загрузки config.json: {e}")
        return {}

# ==========================================
# ПИНГЕР БОТА (Telegram)
# ==========================================

def ping_bot(interval=60):
    """Пингует бота через Telegram API"""
    config = load_config()
    token = config.get("TG_TOKEN", "")
    
    if not token:
        print("[PING] Нет TG_TOKEN, пингер бота не запущен")
        return
    
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    while True:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[PING] Бот активен: {response.json().get('result', {}).get('first_name', 'Бот')}")
            else:
                print(f"[PING] Ошибка: {response.status_code}")
        except Exception as e:
            print(f"[PING] Ошибка соединения: {e}")
        
        time.sleep(interval)

def start_background_pinger(interval=60):
    """Запускает пингер в фоновом потоке"""
    thread = threading.Thread(target=ping_bot, args=(interval,), daemon=True)
    thread.start()
    print(f"[PING] Пингер бота запущен (интервал {interval} сек)")

# ==========================================
# ПИНГЕР АГЕНТА (Flask)
# ==========================================

def ping_agent():
    """Пингует Flask-агента, чтобы он не засыпал"""
    url = "https://ansamb-sledov.ru"  # или http://localhost:10000
    interval = 60
    
    while True:
        try:
            response = requests.get(url, timeout=5)
            print(f"[PING] Агент активен: {response.status_code}")
        except Exception as e:
            print(f"[PING] Ошибка агента: {e}")
        
        time.sleep(interval)

def start_agent_pinger():
    """Запускает пингер агента в фоновом потоке"""
    thread = threading.Thread(target=ping_agent, daemon=True)
    thread.start()
    print("[PING] Пингер агента запущен")

# ==========================================
# ТЕСТ
# ==========================================

if __name__ == "__main__":
    print("=== ТЕСТ PING_UTILS ===")
    config = load_config()
    print(f"Конфиг: {config}")
    print("✅ ping_utils.py готов к работе")
