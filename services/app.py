# ==========================================
# Файл: services/app.py
# Справка: README.md → Веб-морда
# Задача: запуск, подключение модулей, VK OAuth + авто-рефреш
# Комментарий: порт берётся из переменной PORT для совместимости с Bothost
# ==========================================

import os
import sys
import hashlib
import base64
import secrets
import json as json_module
import time as time_module
from flask import Flask, request as flask_request, session, redirect, url_for, jsonify, render_template
from flask_socketio import SocketIO
from debug_utils import debug_log
import requests as req

# === ИСПРАВЛЕНИЕ: корень проекта для Bothost ===
PROJECT_ROOT = '/usr/src/app'
sys.path.insert(0, PROJECT_ROOT)

# Диагностика путей
print("=== DIAGNOSTIC ===")
print("PROJECT_ROOT =", PROJECT_ROOT)
print("Templates path:", os.path.join(PROJECT_ROOT, 'templates'))
print("Static path:", os.path.join(PROJECT_ROOT, 'static'))
print("Templates exists:", os.path.exists(os.path.join(PROJECT_ROOT, 'templates')))
print("Static exists:", os.path.exists(os.path.join(PROJECT_ROOT, 'static')))
print("==================")
# =============================================

from services.app_modules.auth import auth_bp
from services.app_modules.static import static_bp
from services.app_modules.youtube import youtube_bp
from services.app_modules.socket import socketio, messages
from services.app_modules.routes import routes_bp
from services.app_modules.background import background_bp, start_background_thread
from services.web_api import web_api
from services.analytics_api import analytics_api
from services.agent import agent_bp
from services.error_handlers import register_error_handlers

app = Flask(__name__, 
            template_folder=os.path.join(PROJECT_ROOT, 'templates'), 
            static_folder=os.path.join(PROJECT_ROOT, 'static'))

app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
socketio.init_app(app, cors_allowed_origins="*")

# ==========================================
# ЗАЩИТА API И СТРАНИЦ
# ==========================================
@app.before_request
def require_auth():
    public_paths = ['/auth/login', '/auth/check', '/static', '/api/check_auth']
    for path in public_paths:
        if flask_request.path.startswith(path):
            return None
    
    if not session.get('authenticated'):
        if flask_request.path.startswith('/api/') or flask_request.path.startswith('/bg/'):
            return jsonify({'error': 'Unauthorized', 'status': 'error'}), 401
        return redirect(url_for('auth.login'))

@app.route('/api/check_auth')
def check_auth():
    return jsonify({'authenticated': session.get('authenticated', False)})

# ==========================================
# РЕГИСТРАЦИЯ BLUEPRINT'ОВ
# ==========================================
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(static_bp, url_prefix='/static')
app.register_blueprint(youtube_bp, url_prefix='/youtube')
app.register_blueprint(routes_bp, url_prefix='/')
app.register_blueprint(background_bp, url_prefix='/bg')
app.register_blueprint(web_api, url_prefix='/api')
app.register_blueprint(analytics_api, url_prefix='/api/analytics')
app.register_blueprint(agent_bp, url_prefix='/agent')

register_error_handlers(app)

# ==========================================
# VK OAUTH + АВТО-РЕФРЕШ (device_id из переменной)
# ==========================================

_vk_token_cache = {"token": None, "expires_at": 0}

def get_vk_token():
    now = time_module.time()
    if _vk_token_cache["token"] and now < _vk_token_cache["expires_at"]:
        return _vk_token_cache["token"]
    
    token = os.environ.get("VK_TOKEN_USER")
    if token and len(token) > 80:
        _vk_token_cache["token"] = token
        _vk_token_cache["expires_at"] = now + 3000
        debug_log("VK_TOKEN", f"Токен из кэша")
        return token
    
    debug_log("VK_TOKEN", "Токен истёк, пробую рефреш...")
    new_token = refresh_vk_token()
    if new_token:
        _vk_token_cache["token"] = new_token
        _vk_token_cache["expires_at"] = now + 3000
        return new_token
    return None

def refresh_vk_token():
    refresh_token = os.environ.get("VK_REFRESH_TOKEN")
    if not refresh_token:
        debug_log("VK_REFRESH", "VK_REFRESH_TOKEN не задан", "ERROR")
        return None
    
    client_id = os.environ.get("VK_APP_ID")
    client_secret = os.environ.get("VK_APP_SECRET")
    device_id = os.environ.get("VK_DEVICE_ID")
    
    if device_id:
        debug_log("VK_REFRESH", f"device_id из переменной: {device_id[:20]}...")
    else:
        debug_log("VK_REFRESH", "VK_DEVICE_ID не задан", "WARNING")
    
    debug_log("VK_REFRESH", "Запрос рефреша...")
    
    params = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    if device_id:
        params["device_id"] = device_id
    
    try:
        r = req.post("https://id.vk.com/oauth2/auth", data=params, timeout=10)
        data = r.json()
        debug_log("VK_REFRESH", f"Ответ: {str(data)[:200]}")
        
        if "access_token" in data:
            os.environ["VK_TOKEN_USER"] = data["access_token"]
            if "refresh_token" in data:
                os.environ["VK_REFRESH_TOKEN"] = data["refresh_token"]
            debug_log("VK_REFRESH", f"Токен обновлён! Длина: {len(data['access_token'])}", "INFO")
            return data["access_token"]
        else:
            debug_log("VK_REFRESH", f"Ошибка: {data.get('error')}", "ERROR")
            return None
    except Exception as e:
        debug_log("VK_REFRESH", f"Исключение: {e}", "ERROR")
        return None

@app.route('/api/vk/callback')
def vk_callback():
    code = flask_request.args.get('code')
    state = flask_request.args.get('state', '')
    device_id = flask_request.args.get('device_id', '')
    
    if device_id:
        debug_log("VK_OAUTH", f"device_id получен: {device_id[:20]}... Сохрани в VK_DEVICE_ID в Render!")
    
    if not code:
        return "❌ Нет кода авторизации", 400
    
    client_id = os.environ.get("VK_APP_ID")
    client_secret = os.environ.get("VK_APP_SECRET")
    redirect_uri = "https://ansambl-sledov-8.bothost.tech/api/vk/callback"
    
    try:
        with open("/tmp/vk_code_verifier.txt", "r") as f:
            code_verifier = f.read().strip()
    except:
        code_verifier = None
    
    params = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code,
        "state": state
    }
    if device_id:
        params["device_id"] = device_id
    if code_verifier:
        params["code_verifier"] = code_verifier
    
    try:
        r = req.post("https://id.vk.com/oauth2/auth", data=params, timeout=10)
        data = r.json()
        if "access_token" in data:
            return f"""
            <h2>✅ Токен получен!</h2>
            <p><b>Device ID:</b> {device_id}</p>
            <p><b>Access Token:</b><br><textarea rows="3" style="width:100%">{data['access_token']}</textarea></p>
            <p><b>Refresh Token:</b><br><textarea rows="3" style="width:100%">{data.get('refresh_token', '')}</textarea></p>
            <p style="color: green;">Скопируй все три значения в Render.</p>
            """
        else:
            return f"<h2>❌ Ошибка: {data.get('error')}</h2>", 500
    except Exception as e:
        return f"<h2>❌ Ошибка: {e}</h2>", 500

@app.route('/api/vk/auth_link')
def vk_auth_link():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode()
    state = secrets.token_urlsafe(16)
    client_id = os.environ.get("VK_APP_ID")
    redirect_uri = "https://ansambl-sledov-8.bothost.tech/api/vk/callback"
    
    os.makedirs("/tmp", exist_ok=True)
    with open("/tmp/vk_code_verifier.txt", "w") as f:
        f.write(code_verifier)
    
    auth_url = f"https://id.vk.com/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=wall,photos,offline&state={state}&code_challenge={code_challenge}&code_challenge_method=S256"
    
    return f"""
    <h2>🔗 Ссылка для авторизации VK</h2>
    <a href="{auth_url}" target="_blank">{auth_url}</a>
    <p><i>После авторизации скопируй Access Token, Refresh Token и Device ID в Render.</i></p>
    """

start_background_thread()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
