# ==========================================
# Файл: services/app.py
# Справка: README.md → Веб-морда
# Задача: запуск, подключение модулей, VK OAuth + авто-рефреш с логами
# ==========================================

import os, sys, hashlib, base64, secrets, json as json_module, time as time_module
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

app = Flask(__name__, template_folder=os.path.join(PROJECT_ROOT, 'templates'), static_folder=os.path.join(PROJECT_ROOT, 'static'))
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY")
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
# VK OAUTH + АВТО-РЕФРЕШ С ЛОГАМИ
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
        debug_log("VK_TOKEN", f"Токен из кэша, годен до {_vk_token_cache['expires_at']}")
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
    device_id = hashlib.sha256(b"ansamb-sledov-bot-94wz.onrender.com").hexdigest()[:32]
    
    debug_log("VK_REFRESH", "Запрос рефреша...")
    
    try:
        r = req.post("https://id.vk.com/oauth2/auth", data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "device_id": device_id
        }, timeout=10)
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
    if not code: return "❌ Нет кода авторизации", 400
    
    client_id = os.environ.get("VK_APP_ID")
    client_secret = os.environ.get("VK_APP_SECRET")
    redirect_uri = "https://ansamb-sledov-bot-94wz.onrender.com/api/vk/callback"
    
    try:
        with open("/tmp/vk_code_verifier.txt", "r") as f: code_verifier = f.read().strip()
    except: code_verifier = None
    
    params = {"grant_type": "authorization_code", "client_id": client_id, "client_secret": client_secret, "redirect_uri": redirect_uri, "code": code, "state": state}
    if device_id: params["device_id"] = device_id
    if code_verifier: params["code_verifier"] = code_verifier
    
    try:
        r = req.post("https://id.vk.com/oauth2/auth", data=params, timeout=10)
        data = r.json()
        if "access_token" in data:
            return f"""
            <h2>✅ Токен получен!</h2>
            <p><b>Access Token:</b><br><textarea rows="3" style="width:100%">{data['access_token']}</textarea></p>
            <p><b>Refresh Token:</b><br><textarea rows="3" style="width:100%">{data.get('refresh_token', '')}</textarea></p>
            <p style="color: green;">Скопируй в VK_TOKEN_USER и VK_REFRESH_TOKEN в Render.</p>
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
    redirect_uri = "https://ansamb-sledov-bot-94wz.onrender.com/api/vk/callback"
    
    os.makedirs("/tmp", exist_ok=True)
    with open("/tmp/vk_code_verifier.txt", "w") as f: f.write(code_verifier)
    
    auth_url = f"https://id.vk.com/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=wall,photos,offline&state={state}&code_challenge={code_challenge}&code_challenge_method=S256"
    
    return f"""
    <h2>🔗 Ссылка для авторизации VK</h2>
    <a href="{auth_url}" target="_blank">{auth_url}</a>
    <p><i>После авторизации скопируй оба токена в Render.</i></p>
    """

start_background_thread()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
