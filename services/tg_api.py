# ==========================================
# Файл: services/tg_api.py
# Справка: README.md → Веб-морда / Telegram API
# Задача: API для комментариев, ответов и постинга в Telegram
# Комментарий: используется веб-мордой для отправки комментариев и ответов
# Зависит от: flask, telebot, debug_utils
# Вызывается из: services/app.py (blueprint)
# ==========================================

import os
import telebot
from flask import Blueprint, request, jsonify
from debug_utils import debug_log

tg_api_bp = Blueprint('tg_api', __name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))
PUBLISH_CHANNEL = os.environ.get("PUBLISH_CHANNEL", "@qwestomir")

bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

def log_tg(level, message):
    debug_log("TG_API", message, level)

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
    
    if not bot:
        log_tg("ERROR", "Telegram бот не настроен (нет BOT_TOKEN)")
        return jsonify({"status": "error", "error": "Telegram бот не настроен"}), 500
    
    if not chat_id or not text:
        return jsonify({"status": "error", "error": "chat_id и text обязательны"}), 400
    
    try:
        if reply_to:
            log_tg("INFO", f"Ответ на сообщение {reply_to} в чате {chat_id}")
            bot.send_message(chat_id, text, reply_to_message_id=int(reply_to))
        else:
            log_tg("INFO", f"Сообщение в чат {chat_id}")
            bot.send_message(chat_id, text)
        return jsonify({"status": "ok"})
    except Exception as e:
        log_tg("ERROR", f"Ошибка отправки: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@tg_api_bp.route('/send_message', methods=['POST'])
def api_tg_send_message():
    """
    Отправляет личное сообщение пользователю в Telegram.
    Ожидает JSON: {"user_id": 123456789, "text": "текст"}
    """
    data = request.json
    user_id = data.get('user_id')
    text = data.get('text', '').strip()
    
    if not bot:
        log_tg("ERROR", "Telegram бот не настроен")
        return jsonify({"status": "error", "error": "Telegram бот не настроен"}), 500
    
    if not user_id or not text:
        return jsonify({"status": "error", "error": "user_id и text обязательны"}), 400
    
    try:
        log_tg("INFO", f"Личное сообщение пользователю {user_id}")
        bot.send_message(user_id, text)
        return jsonify({"status": "ok"})
    except Exception as e:
        log_tg("ERROR", f"Ошибка отправки: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@tg_api_bp.route('/send_to_channel', methods=['POST'])
def api_tg_send_to_channel():
    """
    Отправляет пост в канал Telegram.
    Ожидает JSON: {"text": "текст", "channel": "@channel"}
    """
    data = request.json
    text = data.get('text', '').strip()
    channel = data.get('channel', PUBLISH_CHANNEL)
    
    if not bot:
        log_tg("ERROR", "Telegram бот не настроен")
        return jsonify({"status": "error", "error": "Telegram бот не настроен"}), 500
    
    if not text:
        return jsonify({"status": "error", "error": "text обязателен"}), 400
    
    try:
        log_tg("INFO", f"Пост в канал {channel}")
        bot.send_message(channel, text, parse_mode='Markdown')
        return jsonify({"status": "ok"})
    except Exception as e:
        log_tg("ERROR", f"Ошибка отправки: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

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
    
    if not bot:
        log_tg("ERROR", "Telegram бот не настроен")
        return jsonify({"status": "error", "error": "Telegram бот не настроен"}), 500
    
    if not chat_id or not photo_url:
        return jsonify({"status": "error", "error": "chat_id и photo_url обязательны"}), 400
    
    try:
        log_tg("INFO", f"Фото в чат {chat_id}")
        bot.send_photo(chat_id, photo_url, caption=caption, parse_mode='Markdown')
        return jsonify({"status": "ok"})
    except Exception as e:
        log_tg("ERROR", f"Ошибка отправки: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@tg_api_bp.route('/pin', methods=['POST'])
def api_tg_pin():
    """
    Закрепляет сообщение в чате/канале Telegram.
    Ожидает JSON: {"chat_id": 123, "message_id": 456}
    """
    data = request.json
    chat_id = data.get('chat_id')
    message_id = data.get('message_id')
    
    if not bot:
        log_tg("ERROR", "Telegram бот не настроен")
        return jsonify({"status": "error", "error": "Telegram бот не настроен"}), 500
    
    if not chat_id or not message_id:
        return jsonify({"status": "error", "error": "chat_id и message_id обязательны"}), 400
    
    try:
        log_tg("INFO", f"Закрепление сообщения {message_id} в чате {chat_id}")
        bot.pin_chat_message(chat_id, message_id)
        return jsonify({"status": "ok"})
    except Exception as e:
        log_tg("ERROR", f"Ошибка: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@tg_api_bp.route('/unpin', methods=['POST'])
def api_tg_unpin():
    """
    Открепляет сообщение в чате/канале Telegram.
    Ожидает JSON: {"chat_id": 123, "message_id": 456}
    """
    data = request.json
    chat_id = data.get('chat_id')
    message_id = data.get('message_id')
    
    if not bot:
        log_tg("ERROR", "Telegram бот не настроен")
        return jsonify({"status": "error", "error": "Telegram бот не настроен"}), 500
    
    if not chat_id or not message_id:
        return jsonify({"status": "error", "error": "chat_id и message_id обязательны"}), 400
    
    try:
        log_tg("INFO", f"Открепление сообщения {message_id} в чате {chat_id}")
        bot.unpin_chat_message(chat_id, message_id)
        return jsonify({"status": "ok"})
    except Exception as e:
        log_tg("ERROR", f"Ошибка: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@tg_api_bp.route('/get_chat_id', methods=['GET'])
def api_tg_get_chat_id():
    """
    Возвращает ID чата по username (или текущий чат).
    Параметр: ?username=@channel
    """
    username = request.args.get('username')
    
    if not bot:
        return jsonify({"status": "error", "error": "Telegram бот не настроен"}), 500
    
    if not username:
        return jsonify({"status": "error", "error": "username обязателен"}), 400
    
    try:
        chat = bot.get_chat(username)
        return jsonify({"status": "ok", "chat_id": chat.id, "title": chat.title})
    except Exception as e:
        log_tg("ERROR", f"Ошибка: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

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
