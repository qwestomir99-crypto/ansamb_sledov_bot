# ==========================================
# Файл: services/app.py
# Справка: README.md → Веб-морда
# Задача: запуск, подключение модулей, WebSocket
# Комментарий: исправлены пути к шаблонам и статике (services/templates/, services/static/)
# Зависит от: flask, flask-socketio, debug_utils, threading
# Вызывается из: Render (web service, start command: gunicorn services.app:app)
# ==========================================

import os
import sys
import threading
from flask import Flask
from flask_socketio import SocketIO
from debug_utils import debug_log

# ==========================================
# 1. Корень services/ (где лежит app.py)
# ==========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==========================================
# 2. Корень проекта (где лежат bot/, services/, library/)
# ==========================================

PROJECT_ROOT = os.path.dirname(BASE_DIR)

# ==========================================
# 3. Добавляем корень в sys.path для импортов
# ==========================================

sys.path.insert(0, PROJECT_ROOT)

# ==========================================
# 4. Импорты модулей
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
# 5. Создаём Flask приложение
# ==========================================

app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),  # ← services/templates/
    static_folder=os.path.join(BASE_DIR, 'static')        # ← services/static/
)

app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY")
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

socketio.init_app(app, cors_allowed_origins="*")

# ==========================================
# 6. Регистрация blueprint'ов
# ==========================================

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(static_bp, url_prefix='/static')
app.register_blueprint(youtube_bp, url_prefix='/youtube')
app.register_blueprint(routes_bp, url_prefix='/')
app.register_blueprint(background_bp, url_prefix='/bg')
app.register_blueprint(web_api, url_prefix='/api')
app.register_blueprint(analytics_api, url_prefix='/api/analytics')

# ==========================================
# 7. Запуск бота в фоновом потоке
# ==========================================

def run_bot():
    """Запуск Telegram-бота в отдельном потоке"""
    try:
        from bot.main import main as bot_main
        debug_log("APP", "Бот запущен в фоновом потоке", "INFO")
        bot_main()
    except ImportError as e:
        debug_log("APP", f"Не удалось запустить бота: {e}", "WARNING")
    except Exception as e:
        debug_log("APP", f"Ошибка при запуске бота: {e}", "ERROR")

if os.environ.get("RUN_BOT", "1") == "1":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

# ==========================================
# 8. Запуск фонового потока сообщений
# ==========================================

start_background_thread()

# ==========================================
# 9. Запуск (для локальной разработки)
# ==========================================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
