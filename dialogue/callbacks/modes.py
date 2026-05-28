# ==========================================
# Файл: dialogue/callbacks/modes.py
# Справка: README.md → Обработчики кнопок / Режимы
# Задача: обработка callback'ов для управления режимами
# Комментарий: вынесен из callbacks.py
# Зависит от: telebot, dialogue.activity_modes, ping_utils, debug_utils
# Вызывается из: callbacks/__init__.py
# ==========================================

import telebot
from dialogue.activity_modes import set_mode
from ping_utils import toggle_ping
from debug_utils import debug_log

def register_modes_callbacks(bot: telebot.TeleBot, config: dict):
    """Регистрирует callback'и для режимов"""
    
    @bot.callback_query_handler(func=lambda call: call.data == "mode_morning")
    def callback_mode_morning(call):
        debug_log("CALLBACK", f"Режим 'Утро' от {call.from_user.id}")
        set_mode("утро")
        bot.answer_callback_query(call.id)
        bot.edit_message_text("🌅 Режим 'Утро' активирован.", chat_id=call.message.chat.id, message_id=call.message.message_id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "mode_day")
    def callback_mode_day(call):
        debug_log("CALLBACK", f"Режим 'День' от {call.from_user.id}")
        set_mode("день")
        bot.answer_callback_query(call.id)
        bot.edit_message_text("☀️ Режим 'День' активирован.", chat_id=call.message.chat.id, message_id=call.message.message_id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "mode_evening")
    def callback_mode_evening(call):
        debug_log("CALLBACK", f"Режим 'Вечер' от {call.from_user.id}")
        set_mode("вечер")
        bot.answer_callback_query(call.id)
        bot.edit_message_text("🌙 Режим 'Вечер' активирован.", chat_id=call.message.chat.id, message_id=call.message.message_id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "mode_night")
    def callback_mode_night(call):
        debug_log("CALLBACK", f"Режим 'Ночь' от {call.from_user.id}")
        set_mode("ночь")
        bot.answer_callback_query(call.id)
        bot.edit_message_text("🌌 Режим 'Ночь' активирован.", chat_id=call.message.chat.id, message_id=call.message.message_id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "toggle_ping")
    def callback_toggle_ping(call):
        debug_log("CALLBACK", f"Переключение пинга от {call.from_user.id}")
        toggle_ping()
        bot.answer_callback_query(call.id)
        bot.edit_message_text("🔄 Пинг переключён.", chat_id=call.message.chat.id, message_id=call.message.message_id)
