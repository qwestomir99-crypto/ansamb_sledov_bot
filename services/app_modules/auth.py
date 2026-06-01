# ==========================================
# Файл: services/app_modules/auth.py
# Справка: README.md → Веб-морда / Авторизация
# Задача: логин, логаут, проверка сессии
# Комментарий: исправлен redirect на routes.index
# Зависит от: flask, debug_utils
# Вызывается из: app_modules/__init__.py
# ==========================================

import os
from flask import Blueprint, request, session, redirect, url_for, render_template, jsonify
from functools import wraps
from debug_utils import debug_log

auth_bp = Blueprint('auth', __name__)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# Определяем базовую директорию проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def log_auth(level, message):
    debug_log("APP_AUTH", message, level)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session.clear()
            session['authenticated'] = True
            session.permanent = True
            log_auth("INFO", "Админ авторизован")
            
            # ✅ ИСПРАВЛЕНО: редирект на routes.index вместо index
            return redirect(url_for('routes.index'))
        else:
            error = 'Неверный пароль'
            log_auth("WARNING", "Неудачная попытка входа")
    return render_template('login.html', error=error)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    log_auth("INFO", "Админ вышел")
    return redirect(url_for('auth.login'))
