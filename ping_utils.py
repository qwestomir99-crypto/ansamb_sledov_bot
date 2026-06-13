# ==========================================
# Файл: ping_utils.py
# Справка: README.md → Пинг
# Задача: keep-alive пинг для Bothost (бот и агент)
# Комментарий: URL берутся из переменных окружения, дефолт на Bothost
# ==========================================

import sys
import os
import requests
import threading
import time
import json
from datetime import datetime

# ===== ФИКС ПУТИ К БИБЛИОТЕКАМ =====
sys.path.insert(0, '/home/c/ch756438/.local/lib/python3.10/site-packages')
# ===================================

from services.secrets_manager import get_secret

CONFIG_FILE = "config.json"

def load_config():
    try:
        if not os.path.exists(CONFIG_FILE):
            print(f"[PING] config.json не найден, использую значения по умолчанию")
            return {}
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[PING] Ошибка загрузки config.json: {e}")
        return {}

def ping_self():
    """Пинг самого бота (веб-морды)"""
    url = get_secret("APP_URL", "https://ansambl-sledov-8.bothost.tech")
    try:
        response = requests.get(f"{url}/health", timeout=10)
        print(f"[PING] Бот пинганулся: {response.status_code}")
    except Exception as e:
        print(f"[PING] Ошибка пинга бота: {e}")

def ping_agent():
    """Пинг агента в безопасном цикле"""
    while True:
        try:
            time.sleep(540)  # 9 минут
            config = load_config()
            agent_enabled = config.get("ping", {}).get("agent_enabled", True)
            agent_url = get_secret("AGENT_HEALTH_URL", "https://ansambl-sledov-8.bothost.tech/health")
            
            if not agent_enabled:
                print("[PING] Пинг агента отключён в конфиге")
                continue
            
            response = requests.get(agent_url, timeout=10)
            print(f"[PING] Агент пинганулся: {response.status_code}")
        except Exception as e:
            print(f"[PING] Ошибка в цикле пинга агента: {e}")

def start_background_pinger(interval=60):
    """Запускает пингер бота в фоновом потоке"""
    def _pinger():
        while True:
            try:
                ping_self()
                time.sleep(interval)
            except Exception as e:
                print(f"[PING] Ошибка в пингере: {e}")
                time.sleep(interval)
    
    thread = threading.Thread(target=_pinger, daemon=True)
    thread.start()
    print(f"[PING] Пингер бота запущен (интервал {interval} сек)")

def start_agent_pinger():
    """Запускает пингер агента в фоновом потоке"""
    thread = threading.Thread(target=ping_agent, daemon=True)
    thread.start()
    print("[PING] Пингер агента запущен")

def toggle_ping():
    """Заглушка для совместимости"""
    return True
