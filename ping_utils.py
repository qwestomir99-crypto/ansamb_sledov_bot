# ==========================================
# Файл: ping_utils.py
# Справка: README.md → Пинг
# Задача: keep-alive пинг для Render (бот и агент)
# Комментарий: гибридная версия с защитой от падений
# ==========================================

import requests
import threading
import time
import json
import os
from datetime import datetime

CONFIG_FILE = "config.json"

def load_config():
    """Безопасная загрузка config.json"""
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
    """Пинг самого бота"""
    try:
        response = requests.get('https://ansamb-sledov-bot-94wz.onrender.com/ping', timeout=10)
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
            agent_url = config.get("ping", {}).get("agent_url", "https://agent-3kek.onrender.com/health")
            
            if not agent_enabled:
                print("[PING] Пинг агента отключён в конфиге")
                continue
            
            response = requests.get(agent_url, timeout=10)
            print(f"[PING] Агент пинганулся: {response.status_code}")
        except Exception as e:
            print(f"[PING] Ошибка в цикле пинга агента: {e}")
            # Продолжаем цикл, не падаем

def start_background_pinger(interval=60):
    """Запускает пингер бота в фоновом потоке"""
    def _pinger():
        while True:
            try:
                ping_self()
                time.sleep(interval)
            except Exception as e:
                print(f"[PING] Ошибка в пингере: {e}")
                time.sleep(interval)  # Не падаем, ждём
    
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
