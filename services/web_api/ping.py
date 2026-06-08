# ==========================================
# Файл: services/web_api/ping.py
# Справка: README.md → Веб-морда / API / Пинг
# Задача: эндпоинты для пинга бота
# Комментарий: добавлена защита @login_required
# Зависит от: flask, debug_utils, ping_utils
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, jsonify
from debug_utils import debug_log
from ping_utils import toggle_ping
from services.app import login_required

ping_bp = Blueprint('ping', __name__)

def log_p(level, message):
    debug_log("WEB_API_PING", message, level)

@ping_bp.route('/toggle', methods=['POST'])
@login_required
def toggle():
    new_state = toggle_ping()
    log_p("INFO", f"Пинг {'включён' if new_state else 'выключён'}")
    return jsonify({"status": "ok", "state": new_state})

@ping_bp.route('/status', methods=['GET'])
@login_required
def status():
    return jsonify({"status": "ok", "state": True})
