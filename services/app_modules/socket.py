# ==========================================
# Файл: services/app_modules/socket.py
# Справка: README.md → Веб-морда / WebSocket
# Задача: WebSocket, сообщения
# Комментарий: вынесено из app.py
# Зависит от: flask, flask-socketio, debug_utils
# Вызывается из: app_modules/__init__.py
# ==========================================

from flask import Blueprint
from flask_socketio import SocketIO, emit
from debug_utils import debug_log
import datetime

socket_bp = Blueprint('socket', __name__)

socketio = SocketIO()  # будет инициализирован в app.py

messages = []

def log_socket(level, message):
    debug_log("APP_SOCKET", message, level)

@socketio.on('connect')
def handle_connect():
    log_socket("INFO", "WebSocket клиент подключён")
    emit('message_history', messages[-50:])

@socketio.on('disconnect')
def handle_disconnect():
    log_socket("INFO", "WebSocket клиент отключён")

@socketio.on('new_message')
def handle_new_message(data):
    data['timestamp'] = datetime.datetime.now().isoformat()
    messages.append(data)
    emit('message_updated', data, broadcast=True)
    log_socket("INFO", f"Новое сообщение от {data.get('source')}: {data.get('text', '')[:50]}")
