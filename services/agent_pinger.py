# ==========================================
# Файл: services/agent_pinger.py
# Справка: README.md → Пингер агента
# Задача: пинговать агента, чтобы он не засыпал
# Комментарий: URL из переменной AGENT_HEALTH_URL, дефолт на Bothost
# ==========================================

import os
import time
import threading
import requests

def ping_agent():
    """Пинг агента каждые 9 минут, чтобы он не засыпал"""
    url = os.getenv("AGENT_HEALTH_URL", "https://ansambl-sledov-8.bothost.tech/health")
    while True:
        time.sleep(540)  # 9 минут
        try:
            r = requests.get(url, timeout=10)
            print(f"[AGENT_PINGER] Пинг успешен: {r.status_code}")
        except Exception as e:
            print(f"[AGENT_PINGER] Ошибка пинга: {e}")

def start_agent_pinger():
    """Запускает поток пинга агента"""
    thread = threading.Thread(target=ping_agent, daemon=True)
    thread.start()
    print("[AGENT_PINGER] Поток пинга агента запущен")
