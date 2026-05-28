# ==========================================
# Файл: dialogue/callbacks/mail.py
# Справка: README.md → Обработчики кнопок / Почта
# Задача: обработка callback'ов для почты
# Комментарий: вынесен из callbacks.py
# Зависит от: telebot, debug_utils
# Вызывается из: callbacks/__init__.py
# ==========================================

import telebot
from debug_utils import debug_log

def register_mail_callbacks(bot: telebot.TeleBot, config: dict):
    """Регистрирует callback'и для почты"""
    
    @bot.callback_query_handler(func=lambda call: call.data == "mail")
    def callback_mail(call):
        debug_log("CALLBACK", f"Почта от {call.from_user.id}")
        bot.edit_message_text(
            "📧 *Почта*\n\nЗдесь будет ваш почтовый ящик.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
