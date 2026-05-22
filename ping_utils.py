# ==========================================
# Файл: ping_utils.py
# Задача: keep-alive пинг для Render (бот и агент)
# Комментарий: запускается из bot.py в потоках.
#              Пинг бота — раз в 60 секунд, агента — раз в 9 минут.
# ==========================================
import requests
import threading
import time
import json

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def ping_self():
    try:
        requests.get('https://ansamb-sledov-bot-94wz.onrender.com/ping', timeout=10)
    except:
        pass

def ping_agent():
    config = load_config()
    agent_enabled = config.get("ping", {}).get("agent_enabled", True)
    agent_url = config.get("ping", {}).get("agent_url", "https://agent-3kek.onrender.com/health")
    
    if not agent_enabled:
        return
    
    while True:
        time.sleep(540)  # 9 минут
        try:
            requests.get(agent_url, timeout=10)
            print("Пинг агента отправлен")
        except:
            pass

def start_background_pinger(interval=60):
    def _pinger():
        while True:
            ping_self()
            time.sleep(interval)
    threading.Thread(target=_pinger, daemon=True).start()

def start_agent_pinger():
    threading.Thread(target=ping_agent, daemon=True).start()
