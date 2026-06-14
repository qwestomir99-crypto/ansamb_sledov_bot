# ==========================================
# Файл: services/agent.py
# Задача: агент для обработки #говори через Yandex GPT
# Комментарий: исправлен keep_alive (URL из переменной окружения)
# ==========================================

import os
import logging
import requests
import threading
import time
from datetime import datetime

# ===== ЗАГРУЗКА .ENV =====
from dotenv import load_dotenv
load_dotenv('../.env')
# ===================================

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "agent.log"), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("yandex_gpt_agent")

API_KEY = os.getenv("YC_API_KEY")
FOLDER_ID = os.getenv("YC_FOLDER_ID")
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

def ask_yandex_gpt(prompt):
    if not API_KEY or not FOLDER_ID:
        logger.error("YC_API_KEY или YC_FOLDER_ID не заданы")
        return "Ошибка: Yandex GPT не настроен"
    
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
        "messages": [{"role": "user", "text": prompt}]
    }
    
    try:
        response = requests.post(YANDEX_GPT_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        answer = result['result']['alternatives'][0]['message']['text']
        logger.info(f"✅ Успешный ответ: {answer[:100]}...")
        return answer
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return "Ошибка при запросе к Yandex GPT"

def keep_alive():
    port = os.getenv("PORT", "10000")
    url = f"http://127.0.0.1:{port}/agent/health"
    while True:
        time.sleep(60)
        try:
            requests.get(url, timeout=5)
            logger.debug("AGENT: Внутренний пинг успешен")
        except Exception as e:
            logger.debug(f"AGENT: Ошибка пинга: {e}")

threading.Thread(target=keep_alive, daemon=True).start()
