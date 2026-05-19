import os
import logging
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ==========================================
# 1. НАСТРОЙКА ЛОГИРОВАНИЯ
# ==========================================

# Создаём папку для логов, если её нет
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Настройка логирования: и в консоль, и в файл
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "agent.log"), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("yandex_gpt_agent")

# ==========================================
# 2. КОНФИГУРАЦИЯ YANDEX GPT
# ==========================================

API_KEY = os.environ.get("YC_API_KEY")
FOLDER_ID = os.environ.get("YC_FOLDER_ID")
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

def log_request_details(prompt, headers, payload):
    """Детально логируем запрос"""
    logger.info("=" * 60)
    logger.info("📤 НОВЫЙ ЗАПРОС К YANDEX GPT")
    logger.info(f"🕐 Время: {datetime.now().isoformat()}")
    logger.info(f"📝 Промпт: {prompt[:200]}{'...' if len(prompt) > 200 else ''}")
    logger.info(f"🔑 API Key: {API_KEY[:10]}... (первые 10 символов)")
    logger.info(f"📁 Folder ID: {FOLDER_ID}")
    logger.info(f"🌐 URL: {YANDEX_GPT_URL}")
    logger.info(f"📦 Payload: {payload}")
    logger.info(f"📋 Headers: Authorization = Api-Key ***, Content-Type = application/json")
    logger.info("=" * 60)

def log_response_details(response):
    """Детально логируем ответ от Yandex GPT"""
    logger.info("=" * 60)
    logger.info("📥 ОТВЕТ ОТ YANDEX GPT")
    logger.info(f"🕐 Время: {datetime.now().isoformat()}")
    logger.info(f"📊 Статус код: {response.status_code}")
    logger.info(f"📄 Текст ответа: {response.text[:500]}{'...' if len(response.text) > 500 else ''}")
    logger.info("=" * 60)

def log_error_details(error, response=None):
    """Детально логируем ошибку"""
    logger.error("=" * 60)
    logger.error("❌ ОШИБКА В YANDEX GPT")
    logger.error(f"🕐 Время: {datetime.now().isoformat()}")
    logger.error(f"🔥 Тип ошибки: {type(error).__name__}")
    logger.error(f"📝 Текст ошибки: {str(error)}")
    if response:
        logger.error(f"📊 Статус код: {response.status_code}")
        logger.error(f"📄 Тело ответа: {response.text[:500]}")
    logger.error("=" * 60)

# ==========================================
# 3. ОСНОВНАЯ ЛОГИКА АГЕНТА
# ==========================================

@app.route('/ask', methods=['POST'])
def ask():
    """Эндпоинт для команды #говори"""
    try:
        # Получаем промпт
        data = request.get_json()
        if not data:
            logger.warning("Пустой запрос или не JSON")
            return jsonify({"error": "no json"}), 400
        
        prompt = data.get('prompt', '')
        if not prompt:
            logger.warning("Поле prompt отсутствует или пустое")
            return jsonify({"error": "no prompt"}), 400
        
        # Проверяем конфигурацию
        if not API_KEY or not FOLDER_ID:
            logger.error("YC_API_KEY или YC_FOLDER_ID не заданы в переменных окружения")
            return jsonify({"error": "Yandex GPT not configured"}), 500
        
        # Формируем запрос к Yandex GPT
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
        
        # Логируем запрос
        log_request_details(prompt, headers, payload)
        
        # Отправляем запрос
        response = requests.post(YANDEX_GPT_URL, headers=headers, json=payload, timeout=30)
        
        # Логируем ответ
        log_response_details(response)
        
        # Проверяем статус
        response.raise_for_status()
        
        # Парсим ответ
        result = response.json()
        answer = result['result']['alternatives'][0]['message']['text']
        
        logger.info(f"✅ Успешный ответ: {answer[:100]}...")
        
        return jsonify({"answer": answer})
    
    except requests.exceptions.RequestException as e:
        log_error_details(e, e.response if hasattr(e, 'response') else None)
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    
    except KeyError as e:
        logger.error(f"❌ Ошибка парсинга JSON от Yandex GPT: отсутствует ключ {e}")
        if 'response' in locals():
            logger.error(f"📄 Содержимое ответа: {response.text}")
        return jsonify({"error": f"Parse error: {str(e)}"}), 500
    
    except Exception as e:
        log_error_details(e)
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Эндпоинт для проверки работоспособности"""
    return jsonify({
        "status": "ok",
        "service": "yandex-gpt-agent",
        "config": {
            "has_api_key": bool(API_KEY),
            "has_folder_id": bool(FOLDER_ID)
        }
    }), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    """Эндпоинт для просмотра логов (только для админа, по секретному токену)"""
    secret = request.args.get('secret')
    if secret != os.environ.get("LOGS_SECRET", "tleem2026"):
        return jsonify({"error": "Forbidden"}), 403
    
    try:
        with open(os.path.join(LOG_DIR, "agent.log"), "r", encoding='utf-8') as f:
            logs = f.read()
        return logs, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 Запуск агента на порту {port}")
    logger.info(f"📁 Логи будут сохраняться в {os.path.join(LOG_DIR, 'agent.log')}")
    app.run(host='0.0.0.0', port=port, debug=False)
