# ==========================================
# Файл: services/web_api/analytics.py
# Справка: README.md → Веб-морда / API / Аналитика
# Задача: API для аналитики (на SQL)
# Комментарий: переписано на SQL вместо файлов
# Зависит от: flask, services.sql_analytics, debug_utils
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, jsonify
from services.sql_analytics import get_activity_by_hour, get_top_errors
from debug_utils import debug_log

analytics_bp = Blueprint('analytics', __name__)

def log_a(level, message):
    debug_log("WEB_API_ANALYTICS", message, level)

@analytics_bp.route('/activity', methods=['GET'])
def activity():
    try:
        data = get_activity_by_hour(hours=24)
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        log_a("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

@analytics_bp.route('/top_errors', methods=['GET'])
def top_errors():
    try:
        data = get_top_errors(limit=5)
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        log_a("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500
