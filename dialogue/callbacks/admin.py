# ==========================================
# Файл: dialogue/callbacks/admin.py
# Справка: README.md → Обработчики кнопок / Админ-панель
# Задача: обработка callback'ов админ-панели
# ==========================================

import telebot
from dialogue.admin_commands import (
    show_admin_panel, show_add_post_ui,
    show_quotes_panel, list_quotes, add_quote_ui, set_quote_interval_ui,
    show_diagnostics, admin_logout
)
from dialogue.admin.posts import handle_vk_post
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
        show_add_post_ui(call, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "vk_post")
    def callback_vk_post(call):
        debug_log("CALLBACK", f"Пост в VK от {call.from_user.id}")
        handle_vk_post(bot, call.message.chat.id, call.message.message_id, call.from_user.id)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "manage_quotes")
    def callback_manage_quotes(call):
        debug_log("CALLBACK", f"Управление цитатами от {call.from_user.id}")
        show_quotes_panel(call, bot)
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
        bot.edit_message_text(
            "❌ Действие отменено.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_admin_menu_keyboard()
        )
        bot.answer_callback_query(call.id)
