# ==========================================
# Файл: dialogue/agent.py
# Справка: README.md → Агент / #говори
# Задача: обработка запросов к Yandex GPT с контекстом из Библиотеки и настроением
# Комментарий: загружает system prompt из library/context.txt
#              Учитывает настроение пользователя (artist, admin, poet, engineer)
# Зависит от: requests, os, json
# Вызывается из: bot.py (ask_agent), admin_commands.py (process_dialog_message)
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

def get_mood_system_prompt(mood):
    """
    Возвращает system prompt для агента на основе настроения.
    Используется, если user_id не передан или настройки не загружены.
    """
    moods = {
        "artist": "Ты — художник-анархист. Говори метафорами, образами, ритмично. Используй цвета, формы, огонь, сеть, тление.",
        "admin": "Ты — строгий администратор. Говори чётко, коротко, структурированно. По делу, без воды.",
        "poet": "Ты — поэт. Говори ритмично, с рифмой, возвышенно. Используй образы и эмоции.",
        "engineer": "Ты — инженер. Говори технично, точно, без лишних эмоций. Только факты и логика."
    }
    return moods.get(mood, moods["artist"])

def ask_agent(prompt, user_id=None):
    """
    Отправляет запрос к Yandex GPT с контекстом Ансамбля и настроением пользователя.
    
    Args:
        prompt: текст запроса
        user_id: ID пользователя (для определения настроения)
    """
    if not YC_API_KEY or not YC_FOLDER_ID:
        debug_log("AGENT", "YC_API_KEY или YC_FOLDER_ID не заданы", "ERROR")
        return "⚙️ Агент не настроен. Проверь переменные окружения."

    # Загружаем общий контекст из Библиотеки
    system_context = load_system_context()
    
    # Определяем настроение пользователя
    user_mood = "artist"  # по умолчанию
    if user_id:
        try:
            from dialogue.user_settings import get_user_mood
            user_mood = get_user_mood(user_id)
            debug_log("AGENT", f"Пользователь {user_id} настроение: {user_mood}", "INFO")
        except ImportError:
            debug_log("AGENT", "user_settings не загружен, использую стандартное настроение", "WARNING")
        except Exception as e:
            debug_log("AGENT", f"Ошибка получения настроения: {e}", "WARNING")
    
    # Получаем system prompt для настроения
    mood_prompt = get_mood_system_prompt(user_mood)
    
    # Формируем сообщения для Yandex GPT
    messages = []
    
    # Сначала добавляем общий контекст Ансамбля
    if system_context:
        messages.append({
            "role": "system",
            "text": system_context
        })
    
    # Затем добавляем промпт настроения
    messages.append({
        "role": "system",
        "text": mood_prompt
    })
    
    # Добавляем вопрос пользователя
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
        debug_log("AGENT", f"Запрос к Yandex GPT (настроение: {user_mood}): {prompt[:100]}...")
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
    print("=== ТЕСТ АГЕНТА ===")
    print("Без настроения (по умолчанию):")
    print(ask_agent(test_prompt))
    print("\nС настроением 'admin':")
    print(ask_agent(test_prompt, user_id=12345))
