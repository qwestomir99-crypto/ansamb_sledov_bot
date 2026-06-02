# ==========================================
# Файл: bot/handlers/talk.py
# Справка: README.md → Обработчики команд / Диалог
# Задача: команда #говори
# Комментарий: вызывает агента (Yandex GPT) с учётом настроения
# Зависит от: dialogue.agent, dialogue.activity_modes
# Вызывается из: bot/handlers/__init__.py
# ==========================================

from debug_utils import debug_log

def register_talk_handler(bot, config):
    @bot.message_handler(func=lambda message: message.text.lower().startswith("#говори"))
    def handle_talk(message):
        from dialogue.activity_modes import should_respond_to_talk
        from dialogue.agent import ask_agent
        
        if not should_respond_to_talk():
            bot.reply_to(message, "🌙 Старший брат отдыхает. Спроси в другой раз.")
            return
        
        # Извлекаем текст после #говори
        phrase = message.text.replace("#говори", "", 1).strip()
        if not phrase:
            bot.reply_to(message, "🗣 *Старший брат:*\nА что ты хотел сказать?")
            return
        
        bot.send_chat_action(message.chat.id, 'typing')
        answer = ask_agent(phrase, user_id=message.from_user.id)
        
        if answer:
            bot.reply_to(message, f"🗣 *Старший брат:*\n{answer}", parse_mode='Markdown')
        else:
            bot.reply_to(message, "🌙 Старший брат отдыхает. Попробуй позже.")
        
        debug_log("TALK", f"User {message.from_user.id}: {phrase[:50]}... → {answer[:50] if answer else 'None'}")
