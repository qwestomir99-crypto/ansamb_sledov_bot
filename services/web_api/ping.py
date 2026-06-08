# ==========================================
# Файл: services/web_api/ping.py
# Справка: README.md → Веб-морда / API / Пинг
# Задача: эндпоинты для пинга бота
# Комментарий: /ping — публичный, не требует авторизации (для keep-alive)
#              /toggle и /status — защищены через login_required
# Зависит от: flask, debug_utils, ping_utils
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, jsonify
from debug_utils import debug_log
from ping_utils import toggle_ping
from services.auth_decorator import login_required

ping_bp = Blueprint('ping', __name__)

def log_p(level, message):
    debug_log("WEB_API_PING", message, level)

# ==========================================
# ПУБЛИЧНЫЙ ЭНДПОИНТ (для keep-alive, без авторизации)
# ==========================================
@ping_bp.route('/', methods=['GET', 'POST'])
def ping():
    """Публичный пинг — для Render keep-alive, не требует логина"""
    log_p("INFO", "Пинг запрос (публичный)")
    return jsonify({"status": "ok", "message": "pong"})

# ==========================================
# ЗАЩИЩЁННЫЕ ЭНДПОИНТЫ (только для админов)
# ==========================================
@ping_bp.route('/toggle', methods=['POST'])
@login_required
def toggle():
    """Переключение пингера (только для админов)"""
    new_state = toggle_ping()
    log_p("INFO", f"Пинг {'включён' if new_state else 'выключён'}")
    return jsonify({"status": "ok", "state": new_state})

@ping_bp.route('/status', methods=['GET'])
@login_required
def status():
    """Статус пингера (только для админов)"""
    return jsonify({"status": "ok", "state": True})
