# ==========================================
# Файл: dialogue/agent.py
# Справка: README.md → Агент / #говори
# Задача: обработка запросов к Yandex GPT с контекстом из Библиотеки
# Комментарий: загружает system prompt из library/context.txt
# Зависит от: requests, os, json
# Вызывается из: bot.py (ask_agent)
# ==========================================

import os
import requests
import json
from debug_utils import debug_log

YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
YC_API_KEY = os.environ.get("YC_API_KEY")
YC_FOLDER_ID = os.environ.get("YC_FOLDER_ID")

CONTEXT_FILE = "library/context.txt"

def load_system_context():
    """Загружает системный промпт из Библиотеки Ансамбля"""
    try:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        debug_log("AGENT", f"Не удалось загрузить контекст: {e}", "WARNING")
        return None

def ask_agent(prompt):
    """Отправляет запрос к Yandex GPT с контекстом Ансамбля"""
    if not YC_API_KEY or not YC_FOLDER_ID:
        debug_log("AGENT", "YC_API_KEY или YC_FOLDER_ID не заданы", "ERROR")
        return "⚙️ Агент не настроен. Проверь переменные окружения."

    system_context = load_system_context()
    
    # Формируем сообщения для Yandex GPT
    messages = []
    if system_context:
        messages.append({
            "role": "system",
            "text": system_context
        })
    messages.append({
        "role": "user",
        "text": prompt
    })
    
    headers = {
        "Authorization": f"Api-Key {YC_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "modelUri": f"gpt://{YC_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 500
        },
        "messages": messages
    }
    
    try:
        debug_log("AGENT", f"Запрос к Yandex GPT: {prompt[:100]}...")
        response = requests.post(YANDEX_GPT_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        answer = result['result']['alternatives'][0]['message']['text']
        debug_log("AGENT", f"Ответ получен: {answer[:100]}...")
        return answer.strip()
        
    except requests.exceptions.RequestException as e:
        debug_log("AGENT", f"Ошибка запроса: {e}", "ERROR")
        return "🌙 Сеть шумит. Старший брат не расслышал. Повтори позже."
    except Exception as e:
        debug_log("AGENT", f"Ошибка: {e}", "ERROR")
        return "❌ Сбой в Разломе. Попробуй ещё раз."

# Для самостоятельного теста
if __name__ == "__main__":
    test_prompt = "Что такое Ансамбль Следов?"
    print(ask_agent(test_prompt))
