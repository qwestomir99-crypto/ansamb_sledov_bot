# ==========================================
# Файл: dialogue/callbacks/__init__.py
# Справка: README.md → Обработчики кнопок / Сборка
# Задача: собирает все модули callbacks в единый регистратор
# Комментарий: импортирует и регистрирует обработчики из модулей
# Зависит от: telebot
# Вызывается из: bot.py
# ==========================================

import telebot
from debug_utils import debug_log

def register_callback_handlers(bot: telebot.TeleBot, config: dict):
    """
    Регистрирует все обработчики callback_data.
    Вызывается из bot.py.
    """
    from .admin import register_admin_callbacks
    # from .quotes import register_quotes_callbacks  # Временно отключено
    from .modes import register_modes_callbacks
    from .alice import register_alice_callbacks
    from .mail import register_mail_callbacks
    from .user import register_user_callbacks
    from .mood import register_mood_callbacks
    from .youtube_upload import register_youtube_upload_callbacks
    
    register_admin_callbacks(bot, config)
    # register_quotes_callbacks(bot, config)  # Временно отключено
    register_modes_callbacks(bot, config)
    register_alice_callbacks(bot, config)
    register_mail_callbacks(bot, config)
    register_user_callbacks(bot, config)
    register_mood_callbacks(bot, config)
    register_youtube_upload_callbacks(bot, config)
    
    debug_log("CALLBACKS", "Все обработчики кнопок зарегистрированы", "INFO")
