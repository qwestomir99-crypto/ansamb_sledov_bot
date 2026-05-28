# ==========================================
# Файл: bot/handlers/admin.py
# Справка: README.md → Обработчики команд / Админ
# Задача: команда #админ
# ==========================================

def register_admin_handler(bot, config):
    @bot.message_handler(func=lambda message: message.text.startswith("#админ"))
    def handle_admin(message):
        from dialogue.admin_commands import handle_admin_command
        handle_admin_command(message, bot)
