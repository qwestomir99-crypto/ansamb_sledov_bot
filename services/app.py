# ==========================================
# Файл: services/app.py
# Справка: README.md → Веб-морда
# Задача: запуск, подключение модулей, WebSocket, VK OAuth (PKCE)
# Комментарий: device_id из переменной VK_DEVICE_ID
# ==========================================

import os
import sys
import hashlib
import base64
import secrets
import json as json_module
from flask import Flask, request as flask_request
from flask_socketio import SocketIO
from debug_utils import debug_log
import requests as req

PROJECT_ROOT = '/opt/render/project/src'
sys.path.insert(0, PROJECT_ROOT)

from services.app_modules.auth import auth_bp
from services.app_modules.static import static_bp
from services.app_modules.youtube import youtube_bp
from services.app_modules.socket import socketio, messages
from services.app_modules.routes import routes_bp
from services.app_modules.background import background_bp, start_background_thread
from services.web_api import web_api
from services.analytics_api import analytics_api
from services.agent import agent_bp

app = Flask(__name__,
    template_folder=os.path.join(PROJECT_ROOT, 'templates'),
    static_folder=os.path.join(PROJECT_ROOT, 'static')
)

app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY")
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

socketio.init_app(app, cors_allowed_origins="*")

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(static_bp, url_prefix='/static')
app.register_blueprint(youtube_bp, url_prefix='/youtube')
app.register_blueprint(routes_bp, url_prefix='/')
app.register_blueprint(background_bp, url_prefix='/bg')
app.register_blueprint(web_api, url_prefix='/api')
app.register_blueprint(analytics_api, url_prefix='/api/analytics')
app.register_blueprint(agent_bp, url_prefix='/agent')

# ==========================================
# VK OAUTH (device_id из переменной VK_DEVICE_ID)
# ==========================================

def get_device_id():
    did = os.environ.get("VK_DEVICE_ID")
    if not did:
        did = secrets.token_hex(16)
        os.environ["VK_DEVICE_ID"] = did
    return did

@app.route('/api/vk/callback')
def vk_callback():
    code = flask_request.args.get('code')
    state = flask_request.args.get('state', '')
    
    if not code:
        return "❌ Нет кода авторизации", 400
    
    client_id = os.environ.get("VK_APP_ID")
    client_secret = os.environ.get("VK_APP_SECRET")
    redirect_uri = "https://ansamb-sledov-bot-94wz.onrender.com/api/vk/callback"
    device_id = get_device_id()
    
    try:
        with open("/tmp/vk_code_verifier.txt", "r") as f:
            code_verifier = f.read().strip()
    except:
        code_verifier = None
    
    token_url = "https://id.vk.com/oauth2/auth"
    params = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code,
        "state": state,
        "device_id": device_id
    }
    if code_verifier:
        params["code_verifier"] = code_verifier
    
    try:
        r = req.post(token_url, data=params, timeout=10)
        data = r.json()
        
        if "access_token" in data:
            access_token = data["access_token"]
            refresh_token = data.get("refresh_token", "")
            user_id = data.get("user_id", "")
            
            debug_log("VK_OAUTH", f"Токен получен! user_id={user_id}, длина={len(access_token)}", "INFO")
            
            return f"""
            <h2>✅ Токен получен!</h2>
            <p><b>User ID:</b> {user_id}</p>
            <p><b>Device ID (сохранён):</b> {device_id}</p>
            <p><b>Access Token:</b><br><textarea rows="3" style="width:100%">{access_token}</textarea></p>
            <p><b>Длина токена:</b> {len(access_token)}</p>
            <p><b>Refresh Token:</b><br><textarea rows="3" style="width:100%">{refresh_token}</textarea></p>
            <p style="color: green; font-weight: bold;">Скопируй access_token и вставь в переменную VK_TOKEN в Render Dashboard.</p>
            <p style="color: blue;">Также добавь VK_DEVICE_ID = {device_id}</p>
            """
        else:
            error = data.get("error", "неизвестная ошибка")
            error_desc = data.get("error_description", "")
            debug_log("VK_OAUTH", f"Ошибка: {error} - {error_desc}", "ERROR")
            return f"<h2>❌ Ошибка: {error}</h2><p>{error_desc}</p><pre>{json_module.dumps(data, indent=2)}</pre>", 500
    except Exception as e:
        debug_log("VK_OAUTH", f"Исключение: {e}", "ERROR")
        return f"<h2>❌ Ошибка: {e}</h2>", 500

@app.route('/api/vk/auth_link')
def vk_auth_link():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()
    
    state = secrets.token_urlsafe(16)
    device_id = get_device_id()
    client_id = os.environ.get("VK_APP_ID")
    redirect_uri = "https://ansamb-sledov-bot-94wz.onrender.com/api/vk/callback"
    
    os.makedirs("/tmp", exist_ok=True)
    with open("/tmp/vk_code_verifier.txt", "w") as f:
        f.write(code_verifier)
    
    auth_url = (
        f"https://id.vk.com/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=wall,photos,offline"
        f"&state={state}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&device_id={device_id}"
    )
    
    return f"""
    <h2>🔗 Ссылка для авторизации VK</h2>
    <p>Device ID: {device_id}</p>
    <p>Открой эту ссылку и разреши доступ:</p>
    <a href="{auth_url}" target="_blank">{auth_url}</a>
    <p><i>После авторизации ты будешь перенаправлен на /api/vk/callback где получишь токен.</i></p>
    """

# ==========================================
# ЗАПУСК ФОНОВОГО ПОТОКА СООБЩЕНИЙ
# ==========================================

start_background_thread()

# ==========================================
# ЗАПУСК (для локальной разработки)
# ==========================================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
