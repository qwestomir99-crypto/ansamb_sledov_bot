import requests
import threading
import time

MAIN_BOT_URL = "https://ansamb-sledov-bot-94wz.onrender.com/ping"

def ping_self():
    """Отправляет запрос на /ping основного бота (для ручного пробуждения)"""
    try:
        requests.get(MAIN_BOT_URL, timeout=10)
    except:
        pass

def start_background_pinger(interval=60):
    """Запускает фоновый пинг каждые N секунд"""
    def _pinger():
        while True:
            ping_self()
            time.sleep(interval)
    threading.Thread(target=_pinger, daemon=True).start()
