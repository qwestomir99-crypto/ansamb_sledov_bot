# ==========================================
# Файл: services/ping_utils.py
# Справка: README.md → Пингер
# Задача: фоновый пинг бота, чтобы он не засыпал
# ==========================================

import time
import os
import threading
import requests

# ==========================================
# ПИНГЕР БОТА (Telegram)
# ==========================================

def ping_bot(interval=60):
    """Пингует бота через Telegram API"""
    token = os.getenv("BOT_TOKEN")
    
    if not token:
        print("[PING] Нет BOT_TOKEN, пингер бота не запущен")
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
    url = os.getenv("AGENT_HEALTH_URL", "https://ansambl-sledov-8.bothost.tech/health")
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
    token = os.getenv("BOT_TOKEN")
    print(f"BOT_TOKEN: {'найден' if token else 'не найден'}")
    print("✅ ping_utils.py готов к работе")
