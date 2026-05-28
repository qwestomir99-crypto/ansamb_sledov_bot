# ==========================================
# Файл: Alice/core.py
# Справка: README.md → Алиса / Ядро
# Задача: генерация ответов Алисы (с фоллбэком на ask_agent)
# Комментарий: Алиса — главный голос. Если она недоступна — отвечает Старший брат.
#              Добавлена возможность предлагать изменения кода.
# Зависит от: dialogue.agent, debug_utils, config.json, services.suggestion_engine
# Вызывается из: bot.py (обработчик #говори)
# ==========================================

import os
import json
from debug_utils import debug_log
from dialogue.agent import ask_agent
from services.suggestion_engine import create_suggestion

def log_alice(level, message):
    debug_log("ALICE", message, level)

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except:
        return {}

def generate_alice_response(user_message, user_id=None):
    """
    Главный метод Алисы.
    Если Алиса включена — отвечает она.
    Если Алиса выключена или недоступна — отвечает Старший брат.
    """
    config = load_config()
    alice_enabled = config.get("alice", {}).get("enabled", False)
    
    if not alice_enabled:
        log_alice("INFO", "Алиса выключена, отвечает Старший брат")
        return ask_agent(user_message, user_id)
    
    try:
        # Здесь будет логика Алисы (промпты, контекст)
        # Пока — заглушка
        response = ask_agent(user_message, user_id)
        log_alice("INFO", f"Алиса ответила: {response[:50]}...")
        return response
    except Exception as e:
        log_alice("ERROR", f"Алиса недоступна: {e}")
        return ask_agent(user_message, user_id)

def suggest_change(description, code_snippet, target_file):
    """
    Алиса предлагает изменение кода.
    Возвращает ID предложения.
    """
    return create_suggestion(description, code_snippet, target_file)
