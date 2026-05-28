# ==========================================
# Файл: services/web_api/__init__.py
# Справка: README.md → Веб-морда / API / Сборка
# Задача: собирает все модули web_api в один blueprint
# Комментарий: импорты и регистрация
# Зависит от: all modules above
# Вызывается из: services/app.py
# ==========================================

from flask import Blueprint
from .quotes import quotes_bp
from .modes import modes_bp
from .ping import ping_bp
from .posts import posts_bp
from .theme import theme_bp
from .alice import alice_bp
from .audit import audit_bp
from .youtube_upload import youtube_upload_bp

web_api = Blueprint('web_api', __name__)

web_api.register_blueprint(quotes_bp, url_prefix='/quotes')
web_api.register_blueprint(modes_bp, url_prefix='/modes')
web_api.register_blueprint(ping_bp, url_prefix='/ping')
web_api.register_blueprint(posts_bp, url_prefix='/posts')
web_api.register_blueprint(theme_bp, url_prefix='/theme')
web_api.register_blueprint(alice_bp, url_prefix='/alice')
web_api.register_blueprint(audit_bp, url_prefix='/audit')
web_api.register_blueprint(youtube_upload_bp, url_prefix='/youtube_upload')
