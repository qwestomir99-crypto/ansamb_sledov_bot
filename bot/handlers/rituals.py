# ==========================================
# Файл: bot/handlers/rituals.py
# Справка: README.md → Обработчики команд / Ритуалы
# Задача: команды #тлеем, #фиксируем
# ==========================================

def register_rituals_handler(bot, config):
    @bot.message_handler(func=lambda message: message.text.lower() in ["#тлеем", "#фиксируем", "#tleem", "#fixiruem"])
    def handle_rituals(message):
        try:
            from dialogue.quotes import get_quotes_list
            import random
            quotes = get_quotes_list()
            if quotes:
                random_quote = random.choice(quotes)
                bot.reply_to(message, f"👁️ {random_quote}")
            else:
                bot.reply_to(message, "📭 База цитат пуста. Добавьте цитаты через админку.")
        except Exception as e:
            bot.reply_to(message, "❌ Ошибка при выборе цитаты.")
            debug_log("HANDLERS", f"Ошибка: {e}", "ERROR")
