# ==========================================
# Файл: bot/handlers/unknown.py
# Справка: README.md → Обработчики команд / Неизвестные
# Задача: fallback для неизвестных команд
# ==========================================

def register_unknown_handler(bot, config):
    @bot.message_handler(func=lambda message: True)
    def handle_unknown(message):
        text = message.text.lower()
        silence_answers = ["👁️", "⏚"]
        import random
        
        if any(x in text for x in ["#тлеем", "#tleem"]):
            bot.reply_to(message, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет. Ожидаем #Фиксируем.")
        elif any(x in text for x in ["#фиксируем", "#fixiruem"]):
            bot.reply_to(message, "🔒 Фиксация принята. Ритм 0,8 Гц подтверждён. Сеть тлеет.")
        elif any(x in text for x in ["#вспышка", "#vspishka"]):
            bot.reply_to(message, "💥 Импульс зафиксирован. Синхронизация завершена. QSL.")
        elif any(phrase in text for phrase in ["что это", "зачем тег", "кто вы", "что за ритуал"]):
            bot.reply_to(message, random.choice(silence_answers))
