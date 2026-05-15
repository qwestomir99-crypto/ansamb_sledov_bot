import requests
import os
import time
import logging

logger = logging.getLogger(__name__)

# --- КОНФИГУРАЦИЯ (из переменных окружения Render) ---
API_KEY = os.environ.get("YC_API_KEY")
FOLDER_ID = os.environ.get("YC_FOLDER_ID")
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

# --- ЛИМИТ ЗАПРОСОВ В ДЕНЬ ---
LIMIT_FILE = "limit_counter.txt"
DAILY_LIMIT = 100

def get_today_date():
    return time.strftime("%Y-%m-%d")

def check_limit():
    if not os.path.exists(LIMIT_FILE):
        return True
    with open(LIMIT_FILE, "r") as f:
        data = f.read().strip().split()
        if len(data) == 2:
            last_date, count = data[0], int(data[1])
            if last_date == get_today_date() and count >= DAILY_LIMIT:
                return False
    return True

def increment_limit():
    count = 1
    if os.path.exists(LIMIT_FILE):
        with open(LIMIT_FILE, "r") as f:
            data = f.read().strip().split()
            if len(data) == 2 and data[0] == get_today_date():
                count = int(data[1]) + 1
    with open(LIMIT_FILE, "w") as f:
        f.write(f"{get_today_date()} {count}")

def ask_alisa(phrase: str) -> str | None:
    if not check_limit():
        return "Лимит запросов на сегодня исчерпан. Попробуй завтра."

    if not API_KEY or not FOLDER_ID:
        logger.error("YC_API_KEY или YC_FOLDER_ID не заданы в переменных окружения Render")
        return None

    # ПРАВИЛЬНЫЕ ЗАГОЛОВКИ ДЛЯ API-КЛЮЧА (x-folder-id НЕ НУЖЕН)
    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 2000
        },
        "messages": [{"role": "user", "text": phrase}]
    }

    try:
        response = requests.post(YANDEX_GPT_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        answer = result['result']['alternatives'][0]['message']['text']
        increment_limit()
        return answer
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса к Yandex GPT: {e}")
        if e.response:
            logger.error(f"Статус: {e.response.status_code}, Тело: {e.response.text}")
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"Ошибка обработки ответа Yandex GPT: {e}")
        return None
