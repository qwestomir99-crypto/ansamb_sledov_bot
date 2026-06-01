# ==========================================
# Файл: services/app_modules/static.py
# Справка: README.md → Веб-морда / Статика
# Задача: раздача статических файлов
# Комментарий: ИСПРАВЛЕН путь к папке static (АБСОЛЮТНЫЙ ПУТЬ на Render) + ДИАГНОСТИКА
# Зависит от: flask
# Вызывается из: app_modules/__init__.py
# ==========================================

from flask import Blueprint, send_from_directory
import os

static_bp = Blueprint('static', __name__)

# Абсолютный путь к папке static на Render
STATIC_DIR = '/opt/render/project/src/static'

# Диагностика: печатаем путь в логи
print(f"=== ДИАГНОСТИКА STATIC ===")
print(f"STATIC_DIR = {STATIC_DIR}")
print(f"Папка существует? {os.path.exists(STATIC_DIR)}")
if os.path.exists(STATIC_DIR):
    print(f"Содержимое: {os.listdir(STATIC_DIR)}")
    css_dir = os.path.join(STATIC_DIR, 'css')
    if os.path.exists(css_dir):
        print(f"CSS содержит: {os.listdir(css_dir)}")
    js_dir = os.path.join(STATIC_DIR, 'js')
    if os.path.exists(js_dir):
        print(f"JS содержит: {os.listdir(js_dir)}")
print(f"==========================")

@static_bp.route('/<path:filename>')
def serve_static(filename):
    """
    Раздача статических файлов из папки services/static/
    Используется абсолютный путь для надёжности.
    """
    print(f"Запрос статики: {filename}")
    print(f"Полный путь: {os.path.join(STATIC_DIR, filename)}")
    return send_from_directory(STATIC_DIR, filename)

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
