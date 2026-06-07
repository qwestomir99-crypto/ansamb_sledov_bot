# ==========================================
# Файл: dialogue/callbacks/admin.py
# Справка: README.md → Обработчики кнопок / Админ-панель
# Задача: обработка callback'ов админ-панели с автоочисткой
# ==========================================

import telebot
from dialogue.admin_commands import show_admin_panel, show_diagnostics, admin_logout, safe_delete
from dialogue.admin.posts import show_add_post_ui, handle_vk_post, set_publish_interval_ui
from dialogue.admin.quotes_admin import show_quotes_panel, handle_quotes_list, handle_quotes_add_start, handle_quotes_interval
from dialogue.button_map import get_admin_menu_keyboard
from debug_utils import debug_log

def register_admin_callbacks(bot: telebot.TeleBot, config: dict):
    
    @bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
    def callback_manage_bot(call):
        debug_log("CALLBACK", f"Админ-панель от {call.from_user.id}")
        show_admin_panel(call, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "add_post")
    def callback_add_post(call):
        debug_log("CALLBACK", f"Добавление поста от {call.from_user.id}")
        safe_delete(call.message, 0)
        show_add_post_ui(call, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "vk_post")
    def callback_vk_post(call):
        debug_log("CALLBACK", f"Пост в VK от {call.from_user.id}")
        safe_delete(call.message, 0)
        handle_vk_post(bot, call.message.chat.id, call.message.message_id, call.from_user.id)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "manage_quotes")
    def callback_manage_quotes(call):
        debug_log("CALLBACK", f"Управление цитатами от {call.from_user.id}")
        show_quotes_panel(call, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "list_quotes")
    def callback_list_quotes(call):
        debug_log("CALLBACK", f"Список цитат от {call.from_user.id}")
        handle_quotes_list(bot, call.message.chat.id, call.message.message_id, call.from_user.id)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "add_quote")
    def callback_add_quote(call):
        debug_log("CALLBACK", f"Добавление цитаты от {call.from_user.id}")
        safe_delete(call.message, 0)
        handle_quotes_add_start(bot, call.message.chat.id, call.message.message_id, call.from_user.id)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "set_quote_interval")
    def callback_set_quote_interval(call):
        debug_log("CALLBACK", f"Интервал цитат от {call.from_user.id}")
        safe_delete(call.message, 0)
        handle_quotes_interval(bot, call.message.chat.id, call.message.message_id, call.from_user.id)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "set_publish_interval")
    def callback_publish_interval(call):
        debug_log("CALLBACK", f"Интервал постов от {call.from_user.id}")
        safe_delete(call.message, 0)
        set_publish_interval_ui(call, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "diagnostics")
    def callback_diagnostics(call):
        debug_log("CALLBACK", f"Диагностика от {call.from_user.id}")
        show_diagnostics(call, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "admin_logout")
    def callback_logout(call):
        debug_log("CALLBACK", f"Выход админа {call.from_user.id}")
        admin_logout(call, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_admin")
    def callback_back_to_admin(call):
        debug_log("CALLBACK", f"Назад в админ-меню от {call.from_user.id}")
        show_admin_panel(call, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "cancel")
    def callback_cancel(call):
        debug_log("CALLBACK", f"Отмена от {call.from_user.id}")
        safe_delete(call.message, 0)
        msg = bot.send_message(call.message.chat.id, "❌ Действие отменено.")
        safe_delete(msg, 3)
        bot.answer_callback_query(call.id)
