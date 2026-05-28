# ==========================================
# Файл: dialogue/callbacks/quotes.py
# Справка: README.md → Обработчики кнопок / Цитаты
# Задача: обработка callback'ов для управления цитатами
# Комментарий: вынесен из callbacks.py
# Зависит от: telebot, dialogue.admin_commands, debug_utils
# Вызывается из: callbacks/__init__.py
# ==========================================

import telebot
from dialogue.admin_commands import list_quotes, add_quote_ui, set_quote_interval_ui
from debug_utils import debug_log

def register_quotes_callbacks(bot: telebot.TeleBot, config: dict):
    """Регистрирует callback'и для цитат"""
    
    @bot.callback_query_handler(func=lambda call: call.data == "list_quotes")
    def callback_list_quotes(call):
        debug_log("CALLBACK", f"Список цитат от {call.from_user.id}")
        list_quotes(call, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "add_quote")
    def callback_add_quote(call):
        debug_log("CALLBACK", f"Добавление цитаты от {call.from_user.id}")
        add_quote_ui(call, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "set_quote_interval")
    def callback_set_quote_interval(call):
        debug_log("CALLBACK", f"Изменение интервала цитат от {call.from_user.id}")
        set_quote_interval_ui(call, bot)
        bot.answer_callback_query(call.id)
