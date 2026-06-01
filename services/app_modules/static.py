# ==========================================
# Файл: services/app_modules/static.py
# Справка: README.md → Веб-морда / Статика
# Задача: раздача статических файлов
# Комментарий: исправлен путь к папке static (на уровень выше)
# Зависит от: flask
# Вызывается из: app_modules/__init__.py
# ==========================================

from flask import Blueprint, send_from_directory
import os

static_bp = Blueprint('static', __name__)

@static_bp.route('/<path:filename>')
def serve_static(filename):
    """
    Раздача статических файлов из папки services/static/
    Путь вычисляется динамически относительно расположения этого файла.
    """
    # Папка static находится на уровень выше, чем app_modules/
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    
    # Добавляем отладочный лог (опционально)
    # print(f"DEBUG: Serving static file: {filename} from {static_dir}")
    
    return send_from_directory(static_dir, filename)

# ==========================================
# Дополнительные маршруты для статики (если нужны)
# ==========================================

@static_bp.route('/css/<path:filename>')
def serve_css(filename):
    """Раздача CSS файлов"""
    return serve_static(f'css/{filename}')

@static_bp.route('/js/<path:filename>')
def serve_js(filename):
    """Раздача JS файлов"""
    return serve_static(f'js/{filename}')

@static_bp.route('/images/<path:filename>')
def serve_images(filename):
    """Раздача изображений"""
    return serve_static(f'images/{filename}')

# ==========================================
# Если нужно отдать корневой файл (например, favicon.ico)
# ==========================================

@static_bp.route('/favicon.ico')
def favicon():
    return serve_static('favicon.ico')
