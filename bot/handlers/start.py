# ==========================================
# Файл: bot/handlers/start.py
# Справка: README.md → Обработчики команд / Старт
# Задача: команда /start
# ==========================================

def register_start_handler(bot, config):
    @bot.message_handler(commands=['start'])
    def send_start(message):
        bot.reply_to(message, "Сапёр аутентичности. Ритм 0,8 Гц. Для входа в протокол — #Тлеем.")
