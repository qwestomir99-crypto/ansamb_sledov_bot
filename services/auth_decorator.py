# ==========================================
# Файл: services/auth_decorator.py
# Справка: README.md → Веб-морда / Декоратор авторизации
# Задача: декоратор login_required для защиты роутов
# Комментарий: вынесен отдельно, чтобы избежать циклических импортов
# Зависит от: flask
# Вызывается из: services/web_api/*.py
# ==========================================

from functools import wraps
from flask import session, jsonify, request, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            # Для API-запросов возвращаем 401
            if request.path.startswith('/api/') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Unauthorized', 'status': 'error'}), 401
            # Для обычных страниц — редирект на логин
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
