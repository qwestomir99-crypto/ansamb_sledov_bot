# ==========================================
# Файл: services/web_api/posts.py
# Справка: README.md → Веб-морда / API / Посты
# Задача: эндпоинты для управления постами
# Комментарий: часть web_api, вынесена в отдельный модуль
# Зависит от: flask, debug_utils, services.supabase_client
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, request, jsonify
from debug_utils import debug_log
from services.supabase_client import db_insert

posts_bp = Blueprint('posts', __name__)

def log_posts(level, message):
    debug_log("WEB_API_POSTS", message, level)

@posts_bp.route('/create', methods=['POST'])
def create_post():
    data = request.json
    platform = data.get('platform')
    text = data.get('text')
    if not platform or not text:
        return jsonify({"status": "error", "error": "Platform и text обязательны"}), 400
    
    try:
        # Сохраняем пост в Supabase
        db_insert('posts', {"text": text, "platform": platform, "status": "draft"})
        log_posts("INFO", f"Пост создан ({platform})")
        return jsonify({"status": "ok", "message": "Пост создан"})
    except Exception as e:
        log_posts("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500
