# ==========================================
# Файл: Alice/core.py
# Справка: README.md → Алиса / Ядро
# Задача: генерация ответов Алисы (с фоллбэком на ask_agent)
# Комментарий: Алиса — главный голос. Если она недоступна — отвечает Старший брат.
#              Добавлена возможность предлагать изменения кода.
#              Алиса может делегировать задачи Старшему брату.
# Зависит от: dialogue.agent, debug_utils, config.json, services.suggestion_engine
# Вызывается из: bot.py (обработчик #говори)
# ==========================================

import os
import json
from debug_utils import debug_log
from dialogue.agent import ask_agent
from services.suggestion_engine import create_suggestion
from Alice.prompts.library import get_context
from Alice.prompts.roles import get_role_context

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
        # Анализируем запрос
        is_technical = any(word in user_message.lower() for word in ["код", "модуль", "api", "бот", "команда", "сценарий", "напиши", "проверь"])
        is_creative = any(word in user_message.lower() for word in ["стих", "песня", "картина", "идея", "метафора", "образ", "настроение"])
        
        # Определяем роль пользователя
        role_context = get_role_context()
        
        # Загружаем контекст библиотеки
        library_context = get_context()
        
        # Формируем базовый промпт
        base_prompt = f"{role_context}\n\n{library_context}\n\nПользователь: {user_message}\n\nАлиса:"
        
        if is_technical:
            # Делегируем техническую задачу Старшему брату
            task = f"Выполни техническую задачу: {user_message}"
            response = ask_agent(task, user_id=user_id)
            log_alice("INFO", f"Алиса делегировала задачу Старшему брату: {response[:50]}...")
            return f"🗣 *Алиса:* Я передала задачу Старшему брату.\n\n{response}"
        elif is_creative:
            # Алиса отвечает сама (творческая задача)
            response = ask_agent(base_prompt, user_id=user_id)
            log_alice("INFO", f"Алиса ответила: {response[:50]}...")
            return response
        else:
            # Обычный запрос — отвечаем через полный промпт
            response = ask_agent(base_prompt, user_id=user_id)
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
