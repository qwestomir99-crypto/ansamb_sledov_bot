# ==========================================
# Файл: dialogue/callbacks/mood.py
# Справка: README.md → Обработчики кнопок / Настроение
# Задача: обработка callback'ов для настроения
# Комментарий: вынесен из callbacks.py
# Зависит от: telebot, dialogue.user_settings, debug_utils
# Вызывается из: callbacks/__init__.py
# ==========================================

import telebot
from dialogue.user_settings import set_user_mood, get_mood_info
from debug_utils import debug_log

def register_mood_callbacks(bot: telebot.TeleBot, config: dict):
    """Регистрирует callback'и для настроения"""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("mood_"))
    def callback_set_mood(call):
        mood = call.data.replace("mood_", "")
        debug_log("CALLBACK", f"Установка настроения {mood} от {call.from_user.id}")
        if set_user_mood(call.from_user.id, mood):
            mood_info = get_mood_info(mood)
            bot.edit_message_text(
                f"✅ Настроение изменено на «{mood_info['name']}».\n\n"
                f"{mood_info['emoji']} {mood_info['description']}",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        else:
            bot.edit_message_text(
                "❌ Не удалось изменить настроение.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "close_mood_menu")
    def callback_close_mood(call):
        debug_log("CALLBACK", f"Закрытие меню настроения от {call.from_user.id}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
