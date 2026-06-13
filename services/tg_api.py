# ==========================================
# Файл: services/tg_api.py
# Справка: README.md → Веб-морда / Telegram API
# Задача: API для комментариев, ответов и постинга в Telegram
# Комментарий: без telebot
# ==========================================

import sys
import os
import requests
from flask import Blueprint, request, jsonify
from debug_utils import debug_log

# ===== ЗАГРУЗКА СЕКРЕТОВ ИЗ БД =====
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.secrets_manager import get_secret
# ===================================

tg_api_bp = Blueprint('tg_api', __name__)

def log_tg(level, message):
    debug_log("TG_API", message, level)

def get_bot_token():
    token = get_secret("BOT_TOKEN")
    if not token:
        log_tg("ERROR", "BOT_TOKEN не задан")
    return token

def get_admin_user_id():
    uid = get_secret("ADMIN_USER_ID")
    return int(uid) if uid else 0

def get_publish_channel():
    channel = get_secret("PUBLISH_CHANNEL")
    return channel if channel else "@qwestomir"

def tg_request(method, params):
    token = get_bot_token()
    if not token:
        return None
    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        r = requests.get(url, params=params, timeout=30)
        data = r.json()
        if data.get("ok"):
            return data.get("result")
        else:
            log_tg("ERROR", f"Telegram API ошибка: {data.get('description', 'неизвестная')}")
            return None
    except Exception as e:
        log_tg("ERROR", f"Ошибка запроса: {e}")
        return None

@tg_api_bp.route('/comment', methods=['POST'])
def api_tg_comment():
    data = request.json
    chat_id = data.get('chat_id')
    text = data.get('text', '').strip()
    reply_to = data.get('reply_to')
    
    if not chat_id or not text:
        return jsonify({"status": "error", "error": "chat_id и text обязательны"}), 400
    
    params = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_to:
        params["reply_to_message_id"] = int(reply_to)
    
    result = tg_request("sendMessage", params)
    if result:
        log_tg("INFO", f"Сообщение отправлено в чат {chat_id}")
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "error": "Ошибка отправки"}), 500

@tg_api_bp.route('/send_message', methods=['POST'])
def api_tg_send_message():
    data = request.json
    user_id = data.get('user_id')
    text = data.get('text', '').strip()
    
    if not user_id or not text:
        return jsonify({"status": "error", "error": "user_id и text обязательны"}), 400
    
    params = {
        "chat_id": user_id,
        "text": text
    }
    result = tg_request("sendMessage", params)
    if result:
        log_tg("INFO", f"Личное сообщение пользователю {user_id}")
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "error": "Ошибка отправки"}), 500

@tg_api_bp.route('/send_to_channel', methods=['POST'])
def api_tg_send_to_channel():
    data = request.json
    text = data.get('text', '').strip()
    channel = data.get('channel', get_publish_channel())
    
    if not text:
        return jsonify({"status": "error", "error": "text обязателен"}), 400
    
    params = {
        "chat_id": channel,
        "text": text,
        "parse_mode": "Markdown"
    }
    result = tg_request("sendMessage", params)
    if result:
        log_tg("INFO", f"Пост в канал {channel}")
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "error": "Ошибка отправки"}), 500

@tg_api_bp.route('/send_photo', methods=['POST'])
def api_tg_send_photo():
    data = request.json
    chat_id = data.get('chat_id')
    photo_url = data.get('photo_url')
    caption = data.get('caption', '').strip()
    
    if not chat_id or not photo_url:
        return jsonify({"status": "error", "error": "chat_id и photo_url обязательны"}), 400
    
    params = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    result = tg_request("sendPhoto", params)
    if result:
        log_tg("INFO", f"Фото в чат {chat_id}")
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "error": "Ошибка отправки"}), 500

@tg_api_bp.route('/pin', methods=['POST'])
def api_tg_pin():
    data = request.json
    chat_id = data.get('chat_id')
    message_id = data.get('message_id')
    
    if not chat_id or not message_id:
        return jsonify({"status": "error", "error": "chat_id и message_id обязательны"}), 400
    
    params = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    result = tg_request("pinChatMessage", params)
    if result:
        log_tg("INFO", f"Закреплено сообщение {message_id}")
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "error": "Ошибка отправки"}), 500

@tg_api_bp.route('/unpin', methods=['POST'])
def api_tg_unpin():
    data = request.json
    chat_id = data.get('chat_id')
    message_id = data.get('message_id')
    
    if not chat_id or not message_id:
        return jsonify({"status": "error", "error": "chat_id и message_id обязательны"}), 400
    
    params = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    result = tg_request("unpinChatMessage", params)
    if result:
        log_tg("INFO", f"Откреплено сообщение {message_id}")
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "error": "Ошибка отправки"}), 500

@tg_api_bp.route('/get_chat_id', methods=['GET'])
def api_tg_get_chat_id():
    username = request.args.get('username')
    
    if not username:
        return jsonify({"status": "error", "error": "username обязателен"}), 400
    
    params = {
        "@username": username
    }
    result = tg_request("getChat", params)
    if result:
        return jsonify({"status": "ok", "chat_id": result.get("id"), "title": result.get("title")})
    else:
        return jsonify({"status": "error", "error": "Ошибка получения"}), 500

if __name__ == "__main__":
    print("TG API модуль загружен")
    print("Доступные эндпоинты:")
    print("  POST /api/tg/comment - ответ на сообщение")
    print("  POST /api/tg/send_message - личное сообщение")
    print("  POST /api/tg/send_to_channel - пост в канал")
    print("  POST /api/tg/send_photo - фото")
    print("  POST /api/tg/pin - закрепить сообщение")
    print("  POST /api/tg/unpin - открепить")
    print("  GET /api/tg/get_chat_id - получить ID чата")
