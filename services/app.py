# ==========================================
# Файл: services/app.py
# Справка: README.md → Веб-морда
# Задача: запуск, подключение модулей, WebSocket
# Комментарий: ФИНАЛЬНАЯ ВЕРСИЯ — ВСЕ ПУТИ ПРАВИЛЬНЫЕ, БОТА НЕТ
# ==========================================

import os
import sys
from flask import Flask
from flask_socketio import SocketIO
from debug_utils import debug_log

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
