# ==========================================
# Файл: bot/handlers/unknown.py
# Справка: README.md → Обработчики команд / Неизвестные
# Задача: fallback для неизвестных команд
# Комментарий: при вводе неизвестной команды предлагает справку
# Зависит от: telebot
# Вызывается из: bot/handlers/__init__.py
# ==========================================

import random

def register_unknown_handler(bot, config):
    @bot.message_handler(func=lambda message: True)
    def handle_unknown(message):
        text = message.text.lower()
        silence_answers = ["👁️", "⏚"]
        
        # Распознаём ритуальные команды даже без хештега
        if any(x in text for x in ["тлеем", "tleem"]):
            bot.reply_to(message, "💥 Используйте `#тлеем` для ритуала.", parse_mode='Markdown')
        elif any(x in text for x in ["фиксируем", "fixiruem"]):
            bot.reply_to(message, "🔒 Используйте `#фиксируем` для фиксации.", parse_mode='Markdown')
        elif any(x in text for x in ["вспышка", "vspishka"]):
            bot.reply_to(message, "⚡ Используйте `#вспышка` для импульса.", parse_mode='Markdown')
        elif any(phrase in text for phrase in ["что это", "зачем тег", "кто вы", "что за ритуал", "как работает"]):
            bot.reply_to(
                message,
                "📖 *Справка*\n\nВведите `#` для интерактивного меню команд.\n\n"
                "Основные команды:\n"
                "• `#тлеем` — случайная цитата\n"
                "• `#фиксируем` — подтверждение ритма\n"
                "• `#вспышка` — импульс\n"
                "• `#дышим` — пинг бота\n"
                "• `#говори <текст>` — диалог с агентом\n"
                "• `#админ <пароль>` — вход в админ-панель",
                parse_mode='Markdown'
            )
        else:
            # Для всего остального — молчание или редкий ответ
            if random.random() < 0.1:  # 10% шанс ответить
                bot.reply_to(message, random.choice(silence_answers))
