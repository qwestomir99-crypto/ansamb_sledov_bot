# ==========================================
# Файл: bot/handlers/help.py
# Справка: README.md → Обработчики команд / Справка
# Задача: команда #
# ==========================================

def register_help_handler(bot, config):
    @bot.message_handler(func=lambda message: message.text == "#")
    def handle_help(message):
        try:
            from dialogue.help_menu import get_help_keyboard
            bot.reply_to(
                message,
                "📖 *Справка по командам*\n\nВыберите команду для подробного описания:",
                reply_markup=get_help_keyboard(),
                parse_mode='Markdown'
            )
        except ImportError:
            bot.reply_to(message, "❌ Модуль справки не загружен")
