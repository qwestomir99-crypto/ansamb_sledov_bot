# ==========================================
# Файл: bot/handlers.py
# Справка: README.md → Бот / Обработчики
# Задача: регистрация обработчиков и колбэков
# ==========================================

from .handlers import register_handlers
from dialogue.callbacks import register_callback_handlers

def register_all_handlers(bot, config):
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    
    print("[HANDLERS] Обработчики и колбэки зарегистрированы")
