# ==========================================
# Файл: services/app_modules/background.py
# Справка: README.md → Веб-морда / Фоновые потоки
# Задача: фоновый поток для получения сообщений из SQLite
# Комментарий: читает из SQLite, автоматически чистит базу
# ==========================================

import sys
import threading
import time
from flask import Blueprint
from debug_utils import debug_log
from services.sqlite_client import get_messages, clean_old_messages
from services.app_modules.socket import socketio, messages

background_bp = Blueprint('background', __name__)

def log_bg(level, message):
    debug_log("APP_BACKGROUND", message, level)

def fetch_messages_periodically():
    """Читает сообщения из SQLite и отправляет в веб-морду"""
    while True:
        try:
            # Читаем последние сообщения из SQLite
            msgs = get_messages(limit=10)
            for msg in msgs:
                if not any(
                    m.get('chat_id') == msg['chat_id'] and
                    m.get('text') == msg['text'] and
                    m.get('timestamp') == msg['timestamp']
                    for m in messages
                ):
                    socketio.emit('message_updated', msg)
                    messages.append(msg)
            # Очищаем старые сообщения (оставляем последние 100)
            clean_old_messages(keep=100)
            # Ограничиваем размер списка в памяти
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
