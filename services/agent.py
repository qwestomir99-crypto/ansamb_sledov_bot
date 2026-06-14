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
from flask import Blueprint, request, jsonify
from datetime import datetime

# ===== ЗАГРУЗКА .ENV =====
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
# ===================================

agent_bp = Blueprint('agent', __name__)

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

def log_request_details(prompt, headers, payload):
    logger.info("=" * 60)
    logger.info("📤 НОВЫЙ ЗАПРОС К YANDEX GPT")
    logger.info(f"🕐 Время: {datetime.now().isoformat()}")
    logger.info(f"📝 Промпт: {prompt[:200]}{'...' if len(prompt) > 200 else ''}")
    logger.info(f"📁 Folder ID: {FOLDER_ID}")
    logger.info(f"🌐 URL: {YANDEX_GPT_URL}")
    logger.info("=" * 60)

def log_response_details(response):
    logger.info("=" * 60)
    logger.info("📥 ОТВЕТ ОТ YANDEX GPT")
    logger.info(f"🕐 Время: {datetime.now().isoformat()}")
    logger.info(f"📊 Статус код: {response.status_code}")
    logger.info(f"📄 Текст ответа: {response.text[:500]}{'...' if len(response.text) > 500 else ''}")
    logger.info("=" * 60)

def log_error_details(error, response=None):
    logger.error("=" * 60)
    logger.error("❌ ОШИБКА В YANDEX GPT")
    logger.error(f"🕐 Время: {datetime.now().isoformat()}")
    logger.error(f"🔥 Тип ошибки: {type(error).__name__}")
    logger.error(f"📝 Текст ошибки: {str(error)}")
    if response:
        logger.error(f"📊 Статус код: {response.status_code}")
        logger.error(f"📄 Тело ответа: {response.text[:500]}")
    logger.error("=" * 60)

@agent_bp.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        if not data:
            logger.warning("Пустой запрос или не JSON")
            return jsonify({"error": "no json"}), 400
        
        prompt = data.get('prompt', '')
        if not prompt:
            logger.warning("Поле prompt отсутствует или пустое")
            return jsonify({"error": "no prompt"}), 400
        
        if not API_KEY or not FOLDER_ID:
            logger.error("YC_API_KEY или YC_FOLDER_ID не заданы")
            return jsonify({"error": "Yandex GPT not configured"}), 500
        
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
        
        log_request_details(prompt, headers, payload)
        response = requests.post(YANDEX_GPT_URL, headers=headers, json=payload, timeout=30)
        log_response_details(response)
        response.raise_for_status()
        result = response.json()
        answer = result['result']['alternatives'][0]['message']['text']
        logger.info(f"✅ Успешный ответ: {answer[:100]}...")
        return jsonify({"answer": answer})
    
    except requests.exceptions.RequestException as e:
        log_error_details(e, e.response if hasattr(e, 'response') else None)
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except KeyError as e:
        logger.error(f"❌ Ошибка парсинга JSON: отсутствует ключ {e}")
        return jsonify({"error": f"Parse error: {str(e)}"}), 500
    except Exception as e:
        log_error_details(e)
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@agent_bp.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "yandex-gpt-agent",
        "config": {
            "has_api_key": bool(API_KEY),
            "has_folder_id": bool(FOLDER_ID)
        }
    }), 200

@agent_bp.route('/logs', methods=['GET'])
def get_logs():
    secret = request.args.get('secret')
    logs_secret = os.getenv("LOGS_SECRET", "tleem2026")
    if secret != logs_secret:
        return jsonify({"error": "Forbidden"}), 403
    try:
        with open(os.path.join(LOG_DIR, "agent.log"), "r", encoding='utf-8') as f:
            logs = f.read()
        return logs, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# ВНУТРЕННИЙ ПИНГ (keep-alive)
# ==========================================

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
