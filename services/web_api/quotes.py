# ==========================================
# Файл: services/web_api/quotes.py
# Справка: README.md → Веб-морда / API / Цитаты
# Задача: эндпоинты для работы с цитатами
# Комментарий: часть web_api, вынесена в отдельный модуль
# Зависит от: flask, debug_utils, services.supabase_client
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, request, jsonify
from debug_utils import debug_log
from services.supabase_client import db_insert, db_select

quotes_bp = Blueprint('quotes', __name__)

def log_q(level, message):
    debug_log("WEB_API_QUOTES", message, level)

@quotes_bp.route('/list', methods=['GET'])
def list_quotes():
    try:
        # Получаем цитаты из Supabase (или из файла)
        result = db_select('quotes', limit=10)
        return jsonify({"status": "ok", "data": result})
    except Exception as e:
        log_q("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

@quotes_bp.route('/add', methods=['POST'])
def add_quote():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({"status": "error", "error": "Текст обязателен"}), 400
    try:
        db_insert('quotes', {"text": text})
        return jsonify({"status": "ok", "message": "Цитата добавлена"})
    except Exception as e:
        log_q("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500
