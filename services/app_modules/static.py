# ==========================================
# Файл: services/app_modules/static.py
# Справка: README.md → Веб-морда / Статика
# Задача: раздача статических файлов
# Комментарий: вынесено из app.py
# Зависит от: flask
# Вызывается из: app_modules/__init__.py
# ==========================================

from flask import Blueprint, send_from_directory

static_bp = Blueprint('static', __name__)

@static_bp.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)
