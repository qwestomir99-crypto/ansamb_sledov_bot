# ==========================================
# Файл: services/app_modules/background.py
# Справка: README.md → Веб-морда / Фоновые потоки
# Задача: фоновый поток для получения сообщений из VK и TG
# Комментарий: исправлены пути, добавлены импорты socketio и messages
# Зависит от: flask, debug_utils, threading, time, sys
# Вызывается из: app_modules/__init__.py
# ==========================================

import sys
import threading
import time
from flask import Blueprint
from debug_utils import debug_log

# Абсолютный путь к services/
SERVICES_DIR = '/opt/render/project/src/services'
sys.path.insert(0, SERVICES_DIR)

# Импортируем socketio и messages из socket.py
from services.app_modules.socket import socketio, messages

background_bp = Blueprint('background', __name__)

def log_bg(level, message):
    debug_log("APP_BACKGROUND", message, level)

def fetch_messages_periodically():
    try:
        import tg_api
        import vk_api
        log_bg("INFO", "tg_api.py и vk_api.py найдены")
    except ImportError as e:
        log_bg("WARNING", f"tg_api.py или vk_api.py не найдены: {e}")
        return
    
    while True:
        try:
            # Telegram
            tg_msgs = tg_api.get_telegram_messages(10)
            for msg in tg_msgs:
                if not any(m.get('chat_id') == msg['chat_id'] and m.get('text') == msg['text'] and m.get('timestamp') == msg['timestamp'] for m in messages):
                    socketio.emit('message_updated', msg)
                    messages.append(msg)
            # VK
            vk_msgs = vk_api.get_vk_messages(10)
            for msg in vk_msgs:
                if not any(m.get('chat_id') == msg['chat_id'] and m.get('text') == msg['text'] and m.get('timestamp') == msg['timestamp'] for m in messages):
                    socketio.emit('message_updated', msg)
                    messages.append(msg)
            # Ограничение размера списка
            if len(messages) > 200:
                messages[:] = messages[-200:]
            time.sleep(10)
        except Exception as e:
            log_bg("ERROR", f"Ошибка в фоновом потоке: {e}")
            time.sleep(30)

def start_background_thread():
    """Запускает фоновый поток для получения сообщений"""
    threading.Thread(target=fetch_messages_periodically, daemon=True).start()
    log_bg("INFO", "Фоновый поток сообщений запущен")
