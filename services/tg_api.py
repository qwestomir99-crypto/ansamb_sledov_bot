# ==========================================
# Файл: services/tg_api.py
# Справка: README.md → Веб-морда / Telegram API
# Задача: API для комментариев, ответов и постинга в Telegram
# Комментарий: без telebot
# ==========================================

import os
import requests
from flask import Blueprint, request, jsonify
from debug_utils import debug_log

tg_api_bp = Blueprint('tg_api', __name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))
PUBLISH_CHANNEL = os.environ.get("PUBLISH_CHANNEL", "@qwestomir")

def log_tg(level, message):
    debug_log("TG_API", message, level)

def tg_request(method, params):
    """Универсальная функция для запросов к Telegram API"""
    if not BOT_TOKEN:
        log_tg("ERROR", "BOT_TOKEN не задан")
        return None
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
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
    """
    Отправляет комментарий (ответ на сообщение) в Telegram.
    Ожидает JSON: {"chat_id": 123456789, "text": "текст", "reply_to": 123}
    """
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
    """
    Отправляет личное сообщение пользователю в Telegram.
    Ожидает JSON: {"user_id": 123456789, "text": "текст"}
    """
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
    """
    Отправляет пост в канал Telegram.
    Ожидает JSON: {"text": "текст", "channel": "@channel"}
    """
    data = request.json
    text = data.get('text', '').strip()
    channel = data.get('channel', PUBLISH_CHANNEL)
    
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
    """
    Отправляет фото в Telegram.
    Ожидает JSON: {"chat_id": 123, "photo_url": "https://...", "caption": "текст"}
    """
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
    """
    Закрепляет сообщение в чате/канале Telegram.
    Ожидает JSON: {"chat_id": 123, "message_id": 456}
    """
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
    """
    Открепляет сообщение в чате/канале Telegram.
    Ожидает JSON: {"chat_id": 123, "message_id": 456}
    """
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
    """
    Возвращает ID чата по username (или текущий чат).
    Параметр: ?username=@channel
    """
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

# ==========================================
# ДЛЯ ТЕСТА
# ==========================================
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
