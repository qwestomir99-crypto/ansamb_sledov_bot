# ==========================================
# Файл: dialogue/callbacks/__init__.py
# Справка: README.md → Обработчики кнопок / Сборка
# Задача: собирает все модули callbacks в единый регистратор
# ==========================================

import telebot
from debug_utils import debug_log

def register_callback_handlers(bot: telebot.TeleBot, config: dict):
    from .admin import register_admin_callbacks
    from .quotes import register_quotes_callbacks
    from .modes import register_modes_callbacks
    from .alice import register_alice_callbacks
    from .mail import register_mail_callbacks
    from .mood import register_mood_callbacks
    from .diagnostics import register_diagnostics_callbacks
    from .youtube_upload import register_youtube_upload_callbacks
    
    register_admin_callbacks(bot, config)
    register_quotes_callbacks(bot, config)
    register_modes_callbacks(bot, config)
    register_alice_callbacks(bot, config)
    register_mail_callbacks(bot, config)
    
    register_mood_callbacks(bot, config)
    register_youtube_upload_callbacks(bot, config)
    register_diagnostics_callbacks(bot, config)
    debug_log("CALLBACKS", "Все обработчики кнопок зарегистрированы", "INFO")
