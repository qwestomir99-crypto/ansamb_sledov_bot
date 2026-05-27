# ==========================================
# Файл: services/app_modules/auth.py
# Справка: README.md → Веб-морда / Авторизация
# Задача: логин, логаут, проверка сессии
# Комментарий: вынесено из app.py
# Зависит от: flask, debug_utils
# Вызывается из: app_modules/__init__.py
# ==========================================

from flask import Blueprint, request, session, redirect, url_for, render_template
from functools import wraps
from debug_utils import debug_log
import os

auth_bp = Blueprint('auth', __name__)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

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
            return redirect(url_for('auth.index'))
        else:
            error = 'Неверный пароль'
            log_auth("WARNING", "Неудачная попытка входа")
    return render_template('login.html', error=error)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    log_auth("INFO", "Админ вышел")
    return redirect(url_for('auth.login'))
