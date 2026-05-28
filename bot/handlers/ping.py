# ==========================================
# Файл: bot/handlers/ping.py
# Справка: README.md → Обработчики команд / Пинг
# Задача: команда #дышим
# ==========================================

def register_ping_handler(bot, config):
    @bot.message_handler(func=lambda message: "#дышим" in message.text.lower())
    def handle_ping(message):
        from ping_utils import ping_self
        ping_self()
