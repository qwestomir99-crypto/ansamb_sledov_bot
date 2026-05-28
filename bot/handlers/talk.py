# ==========================================
# Файл: bot/handlers/talk.py
# Справка: README.md → Обработчики команд / Диалог
# Задача: команда #говори
# ==========================================

def register_talk_handler(bot, config):
    @bot.message_handler(func=lambda message: message.text.startswith("#говори"))
    def handle_talk(message):
        from dialogue.activity_modes import should_respond_to_talk
        from Alice.core import generate_alice_response
        
        if not should_respond_to_talk():
            bot.reply_to(message, "🌙 Старший брат отдыхает. Спроси в другой раз.")
            return
        
        phrase = message.text.replace("#говори", "", 1).strip()
        if not phrase:
            bot.reply_to(message, "🗣 *Старший брат:*\nА что ты хотел сказать?")
            return
        
        bot.send_chat_action(message.chat.id, 'typing')
        answer = generate_alice_response(phrase)
        if answer:
            bot.reply_to(message, f"🗣 *Алиса:*\n{answer}", parse_mode='Markdown')
        else:
            bot.reply_to(message, "🗣 *Алиса:*\nНе отвечаю сейчас. Попробуй позже.")
