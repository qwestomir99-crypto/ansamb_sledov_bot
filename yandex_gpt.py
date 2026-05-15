import os
import requests
import logging

logger = logging.getLogger(__name__)

def ask_gpt(prompt: str) -> str:
    """
    Отправляет запрос к YandexGPT и возвращает ответ.
    Документация: https://yandex.cloud/ru/docs/foundation-models/operations/yandexgpt/create-prompt
    """
    api_key = os.environ.get("YC_API_KEY")
    folder_id = os.environ.get("YC_FOLDER_ID")

    if not api_key or not folder_id:
        logger.error("YC_API_KEY или YC_FOLDER_ID не заданы в переменных окружения")
        return "Ошибка: не заданы переменные окружения"

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 1000
        },
        "messages": [
            {
                "role": "user",
                "text": prompt
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        answer = result['result']['alternatives'][0]['message']['text']
        return answer
    except Exception as e:
        logger.error(f"Ошибка при запросе к YandexGPT: {e}")
        return "Извините, произошла ошибка. Попробуйте позже."
