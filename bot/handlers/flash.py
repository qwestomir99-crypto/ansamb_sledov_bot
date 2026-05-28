# ==========================================
# Файл: bot/handlers/flash.py
# Справка: README.md → Обработчики команд / Вспышка
# Задача: команда #вспышка
# ==========================================

def register_flash_handler(bot, config):
    @bot.message_handler(func=lambda message: message.text.lower() in ["#вспышка", "#vspishka"])
    def handle_flash(message):
        bot.reply_to(message, "⚡ Ты снаружи картины. До погружения. Аутентичность — не маска. Это способ не сдаться.")
