# ==========================================
# Файл: services/web_api/audit.py
# Справка: README.md → Веб-морда / API / Аудит
# Задача: эндпоинты для аудита
# Комментарий: часть web_api, вынесена в отдельный модуль
# Зависит от: flask, debug_utils, debug_audit
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, jsonify
from debug_utils import debug_log
from debug_audit import run_audit
from debug_utils import get_audit_status

audit_bp = Blueprint('audit', __name__)

def log_a(level, message):
    debug_log("WEB_API_AUDIT", message, level)

@audit_bp.route('/run', methods=['POST'])
def run():
    try:
        result = run_audit()
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        log_a("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

@audit_bp.route('/status', methods=['GET'])
def status():
    return jsonify(get_audit_status())
