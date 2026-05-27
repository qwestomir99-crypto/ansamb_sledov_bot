# ==========================================
# Файл: services/ws_client.py
# Справка: README.md → Веб-морда / WebSocket клиент
# Задача: отправка сообщений в веб-морду через WebSocket
# Комментарий: вынесено из bot.py
# Зависит от: socketio, os, debug_utils
# Вызывается из: bot.py (handle_message)
# ==========================================

import os
import socketio
import asyncio
from debug_utils import debug_log

WEBSOCKET_URL = os.environ.get("WEBSOCKET_URL", "https://ansamb-sledov-bot-94wz.onrender.com")

sio = socketio.AsyncClient()

@sio.on('connect')
def on_connect():
    debug_log("WS_CLIENT", "Подключено к веб-морде", "INFO")

@sio.on('disconnect')
def on_disconnect():
    debug_log("WS_CLIENT", "Отключено от веб-морде", "INFO")

async def send_to_web_morda(event, data):
    try:
        await sio.connect(WEBSOCKET_URL)
        await sio.emit(event, data)
        await sio.disconnect()
    except Exception as e:
        debug_log("WS_CLIENT", f"Ошибка отправки: {e}", "ERROR")
