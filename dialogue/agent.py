# ==========================================
# Файл: dialogue/agent.py
# Справка: README.md → Агент / #говори
# Задача: лёгкий агент для Yandex GPT
# Комментарий: УПРОЩЁННАЯ ВЕРСИЯ (без памяти, журнала, эволюции)
#              Полная версия сохранена как agent_full.py.bak
#              URL и ключи — ТОЛЬКО из переменных окружения
# Зависит от: requests, os, debug_utils
# Вызывается из: bot.py (ask_agent), admin_commands.py (process_dialog_message)
# ==========================================

import os
import requests
from debug_utils import debug_log

# ==========================================
# ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (настроить в Render Dashboard)
# ==========================================
YC_API_KEY = os.environ.get("YC_API_KEY")
YC_FOLDER_ID = os.environ.get("YC_FOLDER_ID")
YANDEX_GPT_URL = os.environ.get("YANDEX_GPT_URL", "https://llm.api.cloud.yandex.net/foundationModels/v1/completion")

# ==========================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==========================================
def ask_agent(prompt, user_id=None):
    """
    Отправляет запрос к Yandex GPT и возвращает ответ.
    user_id пока не используется, но оставлен для совместимости.
    """
    if not YC_API_KEY or not YC_FOLDER_ID:
        debug_log("AGENT", "Ключи не заданы", "ERROR")
        return "⚙️ Агент не настроен. Проверь переменные окружения."

    payload = {
        "modelUri": f"gpt://{YC_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 500
        },
        "messages": [{"role": "user", "text": prompt}]
    }

    headers = {
        "Authorization": f"Api-Key {YC_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        debug_log("AGENT", f"Запрос от user {user_id}: {prompt[:80]}...", "INFO")
        r = requests.post(YANDEX_GPT_URL, headers=headers, json=payload, timeout=30)

        if r.status_code != 200:
            debug_log("AGENT", f"Ошибка API: {r.status_code} {r.text[:200]}", "ERROR")
            return "🌙 Сеть шумит. Повтори позже."

        answer = r.json()['result']['alternatives'][0]['message']['text']
        debug_log("AGENT", f"Ответ: {answer[:80]}...", "INFO")
        return answer.strip()

    except Exception as e:
        debug_log("AGENT", f"Ошибка: {e}", "ERROR")
        return "🌙 Сеть шумит. Повтори позже."

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (заглушки для совместимости)
# ==========================================
def agent_visit_url(url, tags=None):
    debug_log("AGENT", f"agent_visit_url временно отключена", "WARNING")
    return False

def get_agent_status():
    return {
        "status": "simplified",
        "message": "Временная упрощённая версия агента (без памяти и эволюции)"
    }

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ АГЕНТА (УПРОЩЁННАЯ ВЕРСИЯ) ===")
    test_prompt = "Привет, как дела?"
    print(f"Вопрос: {test_prompt}")
    print(f"Ответ: {ask_agent(test_prompt, user_id=123456)}")
