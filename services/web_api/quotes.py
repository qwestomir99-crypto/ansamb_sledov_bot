# ==========================================
# Файл: services/web_api/quotes.py
# Справка: README.md → Веб-морда / API / Цитаты
# Задача: эндпоинты для работы с цитатами
# Комментарий: использует services/sqlite_client
# ==========================================

from flask import Blueprint, request, jsonify
from debug_utils import debug_log
from services.sqlite_client import get_quotes_list, add_quote

quotes_bp = Blueprint('quotes', __name__)

def log_q(level, message):
    debug_log("WEB_API_QUOTES", message, level)

@quotes_bp.route('/list', methods=['GET'])
def list_quotes():
    try:
        quotes = get_quotes_list()
        return jsonify({"status": "ok", "data": quotes})
    except Exception as e:
        log_q("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

@quotes_bp.route('/add', methods=['POST'])
def add_quote_endpoint():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({"status": "error", "error": "Текст обязателен"}), 400
    try:
        success = add_quote(text)
        if success:
            return jsonify({"status": "ok", "message": "Цитата добавлена"})
        else:
            return jsonify({"status": "error", "error": "Ошибка сохранения"}), 500
    except Exception as e:
        log_q("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500
