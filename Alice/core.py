# ==========================================
# Файл: Alice/core.py
# Справка: README.md → Алиса / Ядро
# Задача: генерация ответов Алисы (с кэшем и зеркалом)
# Комментарий: добавлена интеграция с аналитикой и маршрутизацией
# Зависит от: dialogue.agent, debug_utils, config.json, services.suggestion_engine, context_mirror, response_cache, sql_analytics
# Вызывается из: bot.py (обработчик #говори), routing_engine.py
# ==========================================

import os
import json
from debug_utils import debug_log
from dialogue.agent import ask_agent
from services.suggestion_engine import create_suggestion
from Alice.prompts.library import get_context
from Alice.prompts.roles import get_role_context
from Alice.context_mirror import update_mirror, get_context_hint
from Alice.response_cache import get_cached_response, save_cached_response
from services.sql_analytics import record_activity

def log_alice(level, message):
    debug_log("ALICE", message, level)

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except:
        return {}

def get_alice_context_for_routing():
    """Возвращает контекст Алисы для маршрутизации"""
    mirror = load_mirror()
    return {
        "tempo": mirror.get("tempo", "normal"),
        "mood": "creative" if len(mirror.get("metaphors", [])) > 3 else "neutral",
        "last_update": mirror.get("last_update", "")
    }

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
    
    # Записываем активность в аналитику
    record_activity("alice", "request", {"user_message": user_message[:50]})
    
    # Определяем роль и настроение (временно заглушка)
    role = "default"
    mood = "neutral"
    
    # Проверяем кэш
    cached = get_cached_response(user_message, role, mood)
    if cached:
        log_alice("INFO", f"Ответ из кэша: {cached[:50]}...")
        return cached
    
    try:
        # Анализируем запрос
        is_technical = any(word in user_message.lower() for word in ["код", "модуль", "api", "бот", "команда", "сценарий", "напиши", "проверь"])
        is_creative = any(word in user_message.lower() for word in ["стих", "песня", "картина", "идея", "метафора", "образ", "настроение"])
        
        # Определяем роль пользователя
        role_context = get_role_context()
        
        # Загружаем контекст библиотеки
        library_context = get_context()
        
        # Загружаем подсказку из зеркала контекста
        mirror_hint = get_context_hint()
        
        # Формируем полный промпт
        full_prompt = f"{role_context}\n\n{library_context}\n\n{mirror_hint}\n\nПользователь: {user_message}\n\nАлиса:"
        
        response = None
        if is_technical:
            # Делегируем техническую задачу Старшему брату
            task = f"Выполни техническую задачу: {user_message}"
            response = ask_agent(task, user_id=user_id)
        elif is_creative:
            # Алиса отвечает сама (творческая задача)
            response = ask_agent(full_prompt, user_id=user_id)
        else:
            # Обычный запрос — отвечаем через полный промпт
            response = ask_agent(full_prompt, user_id=user_id)
        
        # Сохраняем в кэш
        save_cached_response(user_message, role, mood, response)
        
        # Обновляем зеркало контекста
        update_mirror(user_message, response)
        
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

def reconfigure_agent(new_rules):
    """
    Алиса перенастраивает агента через предложение.
    """
    return suggest_change("Перенастройка агента", new_rules, "Alice/agent_rules.txt")
