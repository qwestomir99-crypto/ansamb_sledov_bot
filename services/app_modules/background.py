# ==========================================
# Файл: services/app_modules/background.py
# Справка: README.md → Веб-морда / Фоновые потоки
# Задача: фоновый поток для получения сообщений из VK и TG
# Комментарий: вынесено из app.py
# Зависит от: flask, debug_utils
# Вызывается из: app_modules/__init__.py
# ==========================================

from flask import Blueprint
from debug_utils import debug_log
import threading
import time

background_bp = Blueprint('background', __name__)

def log_bg(level, message):
    debug_log("APP_BACKGROUND", message, level)

def fetch_messages_periodically():
    try:
        from services.tg_api import get_telegram_messages
        from services.vk_api import get_vk_messages
    except ImportError:
        log_bg("WARNING", "tg_api.py или vk_api.py не найдены, поток отключён")
        return
    
    while True:
        try:
            global messages
            tg_msgs = get_telegram_messages(10)
            for msg in tg_msgs:
                if not any(m.get('chat_id') == msg['chat_id'] and m.get('text') == msg['text'] and m.get('timestamp') == msg['timestamp'] for m in messages):
                    socketio.emit('message_updated', msg)
                    messages.append(msg)
            vk_msgs = get_vk_messages(10)
            for msg in vk_msgs:
                if not any(m.get('chat_id') == msg['chat_id'] and m.get('text') == msg['text'] and m.get('timestamp') == msg['timestamp'] for m in messages):
                    socketio.emit('message_updated', msg)
                    messages.append(msg)
            if len(messages) > 200:
                messages[:] = messages[-200:]
            time.sleep(10)
        except Exception as e:
            log_bg("ERROR", str(e))
            time.sleep(30)
