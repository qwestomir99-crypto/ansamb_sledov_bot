# ==========================================
# Файл: services/web_api/theme.py
# Справка: README.md → Веб-морда / API / Темы
# Задача: эндпоинты для управления темами
# Комментарий: часть web_api, вынесена в отдельный модуль
# Зависит от: flask, debug_utils, services.theme
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, request, jsonify
from debug_utils import debug_log
from services.theme import save_theme

theme_bp = Blueprint('theme', __name__)

def log_t(level, message):
    debug_log("WEB_API_THEME", message, level)

@theme_bp.route('/set', methods=['POST'])
def set_theme():
    data = request.json
    theme = data.get('theme')
    if theme not in ['macos.css', 'dark.css']:
        return jsonify({"status": "error", "error": "Invalid theme"}), 400
    save_theme(theme)
    log_t("INFO", f"Тема изменена на {theme}")
    return jsonify({"status": "ok", "theme": theme})
