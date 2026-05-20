# ==========================================
# Файл: services/agent_pinger.py
# Справка: README.md → Пингер агента
# Задача: пинговать агента, чтобы он не засыпал на бесплатном тарифе Render
# Комментарий: запускается отдельным потоком из bot.py
# Зависит от: requests, threading
# Вызывается из: bot.py
# ==========================================

import time
import threading
import requests

AGENT_URL = "https://agent-3kek.onrender.com"
PING_INTERVAL = 60  # секунд

def ping_agent():
    """Пинг агента каждые N секунд, чтобы он не засыпал"""
    while True:
        time.sleep(PING_INTERVAL)
        try:
            r = requests.get(AGENT_URL, timeout=5)
            print(f"[AGENT_PINGER] Пинг успешен: {r.status_code}")
        except Exception as e:
            print(f"[AGENT_PINGER] Ошибка пинга: {e}")

def start_agent_pinger():
    """Запускает поток пинга агента"""
    thread = threading.Thread(target=ping_agent, daemon=True)
    thread.start()
    print("[AGENT_PINGER] Поток пинга агента запущен")
