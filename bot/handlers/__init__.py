# ==========================================
# Файл: bot/handlers/__init__.py
# Справка: README.md → Обработчики команд / Сборка
# Задача: собирает все модули handlers в единый регистратор
# Комментарий: импортирует и экспортирует register_handlers
# Зависит от: .start, .help, .menu, .admin, .debug, .youtube_test, .talk, .rituals, .flash, .reset, .mood, .ping, .unknown
# Вызывается из: bot/handlers.py
# ==========================================

import telebot
from debug_utils import debug_log

def register_handlers(bot: telebot.TeleBot, config: dict):
    from .start import register_start_handler
    from .help import register_help_handler
    from .menu import register_menu_handler
    from .admin import register_admin_handler
    from .debug import register_debug_handler
    from .youtube_test import register_youtube_test_handler
    from .talk import register_talk_handler
    from .rituals import register_rituals_handler
    from .flash import register_flash_handler
    from .reset import register_reset_handler
    from .mood import register_mood_handler
    from .ping import register_ping_handler
    from .unknown import register_unknown_handler
    
    register_start_handler(bot, config)
    register_help_handler(bot, config)
    register_menu_handler(bot, config)
    register_admin_handler(bot, config)
    register_debug_handler(bot, config)
    register_youtube_test_handler(bot, config)
    register_talk_handler(bot, config)
    register_rituals_handler(bot, config)
    register_flash_handler(bot, config)
    register_reset_handler(bot, config)
    register_mood_handler(bot, config)
    register_ping_handler(bot, config)
    register_unknown_handler(bot, config)
    
    debug_log("HANDLERS", "Все обработчики команд зарегистрированы", "INFO")
