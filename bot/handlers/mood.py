# ==========================================
# Файл: bot/handlers/mood.py
# Справка: README.md → Обработчики команд / Настроение
# Задача: команда #настроение
# ==========================================

def register_mood_handler(bot, config):
    @bot.message_handler(func=lambda message: message.text.lower() == "#настроение")
    def handle_mood(message):
        from dialogue.admin_commands import is_admin_authorized
        from dialogue.button_map import get_moods_keyboard
        
        if not is_admin_authorized(message.from_user.id):
            bot.reply_to(message, "❌ Только для админа")
            return
        
        bot.send_message(
            message.chat.id,
            "🎭 *Выбери настроение:*",
            parse_mode='Markdown',
            reply_markup=get_moods_keyboard()
        )
