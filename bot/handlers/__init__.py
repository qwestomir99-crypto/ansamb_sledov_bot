# ==========================================
# Файл: bot/handlers/__init__.py
# Справка: README.md → Обработчики команд / Сборка
# Задача: собирает все модули handlers в единый регистратор
# Комментарий: импортирует и экспортирует register_handlers и register_all_handlers
# ==========================================

import telebot
from debug_utils import debug_log

def register_handlers(bot: telebot.TeleBot, config: dict):
    from .start import register_start_handler
    from .help import register_help_handler
    from .menu import register_menu_handler
    from .debug import register_debug_handler
    from .youtube_test import register_youtube_test_handler
    from .talk import register_talk_handler
    from .rituals import register_rituals_handler
    from .flash import register_flash_handler
    from .reset import register_reset_handler
    from .mood import register_mood_handler
    from .ping import register_ping_handler
    from .unknown import register_unknown_handler
    
    @bot.message_handler(func=lambda message: message.text.startswith("#админ"))
    def handle_admin(message):
        try:
            from dialogue.admin_commands import handle_admin_command
            handle_admin_command(message, bot)
        except Exception as e:
            debug_log("ADMIN", f"Ошибка в handle_admin: {e}", "ERROR")
            bot.reply_to(message, "❌ Ошибка при открытии админ-панели")
    
    register_start_handler(bot, config)
    register_help_handler(bot, config)
    register_menu_handler(bot, config)
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


def register_all_handlers(bot, config):
    """Регистрирует обработчики + колбэки. Потоки запускаются отдельно."""
    from dialogue.callbacks import register_callback_handlers
    
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    
    print("[HANDLERS] Обработчики и колбэки зарегистрированы")
