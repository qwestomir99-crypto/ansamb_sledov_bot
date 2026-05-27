# ==========================================
# Файл: services/analytics_api.py
# Справка: README.md → Веб-морда / Аналитика API
# Задача: API эндпоинты для аналитики
# Комментарий: вынесено из web_api.py для чистоты
# Зависит от: flask, services.analytics, debug_utils
# Вызывается из: services/app.py (blueprint)
# ==========================================

from flask import Blueprint, jsonify
from debug_utils import debug_log
from services.analytics import get_activity_by_hour, get_top_errors, get_activity_summary

analytics_api = Blueprint('analytics_api', __name__)

def log_analytics_api(level, message):
    debug_log("ANALYTICS_API", message, level)

@analytics_api.route('/activity', methods=['GET'])
def api_analytics_activity():
    try:
        data = get_activity_by_hour(hours=24)
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        log_analytics_api("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

@analytics_api.route('/top_errors', methods=['GET'])
def api_analytics_top_errors():
    try:
        data = get_top_errors(limit=5)
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        log_analytics_api("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

@analytics_api.route('/summary', methods=['GET'])
def api_analytics_summary():
    try:
        data = get_activity_summary()
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        log_analytics_api("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500
