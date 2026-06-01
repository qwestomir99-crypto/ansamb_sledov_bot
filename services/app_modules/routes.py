# ==========================================
# Файл: services/app_modules/routes.py
# Справка: README.md → Веб-морда / Маршруты
# Задача: основные маршруты (index, timeline, ping)
# Комментарий: исправлен импорт THEME_CSS → get_current_theme
# Зависит от: flask, debug_utils
# Вызывается из: app_modules/__init__.py
# ==========================================

from flask import Blueprint, render_template, jsonify
from debug_utils import debug_log
from .auth import login_required
import os
import datetime
from services.theme import get_current_theme

routes_bp = Blueprint('routes', __name__)

def log_r(level, message):
    debug_log("APP_ROUTES", message, level)

QUOTES_FILE = "dialogue/data/quotes.txt"

def get_quotes():
    try:
        with open(QUOTES_FILE, "r", encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()][-10:]
    except:
        return []

@routes_bp.route('/')
@login_required
def index():
    log_r("INFO", "Главная страница загружена")
    return render_template('admin.html', 
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        quotes=get_quotes(),
        theme=get_current_theme()
    )

@routes_bp.route('/timeline')
@login_required
def timeline():
    timeline_path = os.path.join(os.path.dirname(__file__), '..', '..', 'library', 'timeline.md')
    try:
        with open(timeline_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = f"# Таймлайн\n\nОшибка загрузки: {e}"
    return render_template('timeline.html', 
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        content=content,
        theme=get_current_theme()
    )

@routes_bp.route('/ping')
def ping():
    return {"status": "ok", "service": "web-morda + youtube proxy"}, 200
