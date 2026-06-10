# ==========================================
# Файл: services/web_server.py
# Задача: веб-морда для сообщений из VK/Telegram и ответов
# Комментарий: переписан как Flask Blueprint для интеграции с services/app.py
# ==========================================

import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from services.auth_decorator import login_required

web_server_bp = Blueprint('web_server', __name__)

_pending_messages = []

def broadcast_message(message):
    _pending_messages.append(message)
    if len(_pending_messages) > 1000:
        _pending_messages.pop(0)

@web_server_bp.route('/logs/admin')
@login_required
def admin_log():
    if os.path.exists("admin.log"):
        with open("admin.log", "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()[-5000:]
    else:
        content = "Лог не найден"
    return f"<pre style='background:#111; color:#0f0; padding:1rem; overflow:auto'>{content}</pre>"

@web_server_bp.route('/logs/error')
@login_required
def error_log():
    if os.path.exists("error.log"):
        with open("error.log", "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()[-5000:]
    else:
        content = "Лог не найден"
    return f"<pre style='background:#111; color:#f00; padding:1rem; overflow:auto'>{content}</pre>"

@web_server_bp.route('/api/vk/messages')
@login_required
def get_vk_messages():
    limit = request.args.get('limit', 50, type=int)
    return jsonify({"messages": _pending_messages[-limit:]})

@web_server_bp.route('/api/vk/send', methods=['POST'])
@login_required
def send_vk_message_api():
    data = request.json
    vk_token = os.environ.get("VK_TOKEN")
    if not vk_token:
        return jsonify({"status": "error", "message": "VK_TOKEN не задан"}), 500
    peer_id = data.get("peer_id")
    text = data.get("message")
    if not peer_id or not text:
        return jsonify({"status": "error", "message": "peer_id и message обязательны"}), 400
    try:
        import requests
        params = {"access_token": vk_token, "v": "5.199", "peer_id": peer_id, "message": text, "random_id": 0}
        r = requests.get("https://api.vk.com/method/messages.send", params=params, timeout=10)
        data = r.json()
        if 'response' in data:
            return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "message": data.get('error', {}).get('error_msg', 'неизвестная')}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
