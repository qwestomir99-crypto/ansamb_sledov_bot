# ==========================================
# Файл: services/app.py
# Справка: README.md → Веб-морда
# Задача: запуск, подключение модулей, WebSocket, VK OAuth
# Комментарий: ВЕРСИЯ С АГЕНТОМ (полная) + VK callback
# ==========================================

import os
import sys
from flask import Flask, request as flask_request
from flask_socketio import SocketIO
from debug_utils import debug_log
import requests as req

# ==========================================
# КОРЕНЬ ПРОЕКТА (на Render)
# ==========================================

PROJECT_ROOT = '/opt/render/project/src'
sys.path.insert(0, PROJECT_ROOT)

# ==========================================
# ИМПОРТЫ
# ==========================================

from services.app_modules.auth import auth_bp
from services.app_modules.static import static_bp
from services.app_modules.youtube import youtube_bp
from services.app_modules.socket import socketio, messages
from services.app_modules.routes import routes_bp
from services.app_modules.background import background_bp, start_background_thread
from services.web_api import web_api
from services.analytics_api import analytics_api
from services.agent import agent_bp

# ==========================================
# FLASK ПРИЛОЖЕНИЕ С ПРАВИЛЬНЫМИ ПУТЯМИ
# ==========================================

app = Flask(__name__,
    template_folder=os.path.join(PROJECT_ROOT, 'templates'),
    static_folder=os.path.join(PROJECT_ROOT, 'static')
)

app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY")
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

socketio.init_app(app, cors_allowed_origins="*")

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

# ==========================================
# VK OAUTH CALLBACK
# ==========================================

@app.route('/api/vk/callback')
def vk_callback():
    code = flask_request.args.get('code')
    if not code:
        return "❌ Нет кода авторизации", 400
    
    client_id = os.environ.get("VK_APP_ID")
    client_secret = os.environ.get("VK_APP_SECRET")
    redirect_uri = "https://ansamb-sledov-bot-94wz.onrender.com/api/vk/callback"
    
    token_url = "https://id.vk.com/oauth2/auth"
    params = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code
    }
    
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
            <p><b>Access Token (первые 20):</b> {access_token[:20]}...</p>
            <p><b>Длина токена:</b> {len(access_token)}</p>
            <p><b>Refresh Token (первые 20):</b> {refresh_token[:20] if refresh_token else 'нет'}...</p>
            <p style="color: green; font-weight: bold;">Скопируй access_token и вставь в переменную VK_TOKEN в Render Dashboard.</p>
            <p>После перезапуска VK-постинг заработает.</p>
            <p><i>Токен живёт 1 час, refresh_token — 180 дней.</i></p>
            """
        else:
            error = data.get("error", "неизвестная ошибка")
            error_desc = data.get("error_description", "")
            debug_log("VK_OAUTH", f"Ошибка: {error} - {error_desc}", "ERROR")
            return f"<h2>❌ Ошибка: {error}</h2><p>{error_desc}</p><pre>{data}</pre>", 500
    except Exception as e:
        debug_log("VK_OAUTH", f"Исключение: {e}", "ERROR")
        return f"<h2>❌ Ошибка: {e}</h2>", 500

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
