# ==========================================
# Файл: dialogue/callbacks/quotes.py
# Справка: README.md → Обработчики кнопок / Цитаты
# Задача: управление цитатами (список, добавление, интервал)
# Комментарий: состояния вынесены в state_manager
# ==========================================

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.button_map import get_text, get_callback, get_admin_menu_keyboard
from dialogue.quotes import get_quotes_list, add_quote, set_quotes_interval, get_quotes_interval
from debug_utils import debug_log
from dialogue.state_manager import user_states

def register_quotes_callbacks(bot, config):
    
    @bot.callback_query_handler(func=lambda call: call.data == "manage_quotes")
    def quotes_panel(call):
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(get_text("list_quotes"), callback_data=get_callback("list_quotes")),
            InlineKeyboardButton(get_text("add_quote"), callback_data=get_callback("add_quote")),
        )
        keyboard.add(
            InlineKeyboardButton(get_text("set_quote_interval"), callback_data=get_callback("set_quote_interval")),
            InlineKeyboardButton(get_text("back_to_admin"), callback_data=get_callback("back_to_admin")),
        )
        bot.edit_message_text(
            "📜 *Управление цитатами*\n\n"
            f"📊 Всего цитат: {len(get_quotes_list())}\n"
            f"⏱️ Интервал публикации: {get_quotes_interval()} мин.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "list_quotes")
    def list_quotes(call):
        quotes = get_quotes_list()
        if not quotes:
            bot.edit_message_text(
                "📭 База цитат пуста.\n\nДобавьте цитаты через #админ.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(get_text("back_to_admin"), callback_data=get_callback("back_to_admin"))
                )
            )
            return
        
        text = "📖 *Последние 20 цитат:*\n\n"
        for i, q in enumerate(quotes[-20:], 1):
            text += f"{i}. {q[:80]}{'...' if len(q) > 80 else ''}\n"
        
        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(get_text("back_to_admin"), callback_data=get_callback("back_to_admin"))
            ),
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "add_quote")
    def add_quote_ui(call):
        user_id = call.from_user.id
        user_states[user_id] = "waiting_quote_text"
        bot.edit_message_text(
            "📜 *Добавление цитаты*\n\n"
            "Введите текст цитаты (можно на нескольких строках).\n"
            "/cancel — отмена",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "set_quote_interval")
    def set_interval_ui(call):
        user_id = call.from_user.id
        user_states[user_id] = "waiting_quote_interval"
        bot.edit_message_text(
            f"⏱️ *Текущий интервал цитат:* {get_quotes_interval()} мин.\n\n"
            "Введите новое значение в минутах (число от 5 до 720).\n"
            "/cancel — отмена",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_admin")
    def back_to_admin(call):
        from dialogue.callbacks.admin import show_admin_panel
        show_admin_panel(call)
