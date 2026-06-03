# ==========================================
# Файл: dialogue/callbacks/admin.py
# Справка: README.md → Обработчики кнопок / Админ
# Задача: обработка кнопок админ-меню (главное меню)
# Комментарий: исправлен импорт (удалён state_manager)
# ==========================================

import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.button_map import get_admin_menu_keyboard
from debug_utils import debug_log

def auto_delete_menu(bot, chat_id, message_id, delay=720):
    """Удаляет сообщение через delay секунд (720 = 12 минут)"""
    def _delete():
        time.sleep(delay)
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
    threading.Thread(target=_delete, daemon=True).start()

def register_admin_callbacks(bot, config):
    
    @bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
    def show_admin_panel(call):
        bot.edit_message_text(
            "🛡️ *Админ-панель*\n\nВыберите действие:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_admin_menu_keyboard(),
            parse_mode='Markdown'
        )
        auto_delete_menu(bot, call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    # ==========================================
    # ДОБАВЛЕНИЕ ПОСТА (в пул)
    # ==========================================
    @bot.callback_query_handler(func=lambda call: call.data == "add_post")
    def add_post_ui(call):
        from dialogue.admin_commands import show_add_post_ui
        show_add_post_ui(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == "cancel_add_post")
    def cancel_post(call):
        from dialogue.admin_commands import cancel_add_post
        cancel_add_post(call, bot)
    
    # ==========================================
    # ПОСТ В VK (прямая публикация)
    # ==========================================
    @bot.callback_query_handler(func=lambda call: call.data == "vk_post")
    def vk_post_ui(call):
        from dialogue.admin_commands import show_vk_post_ui
        show_vk_post_ui(call, bot)
    
    # ==========================================
    # УПРАВЛЕНИЕ ЦИТАТАМИ
    # ==========================================
    @bot.callback_query_handler(func=lambda call: call.data == "manage_quotes")
    def quotes_panel(call):
        from dialogue.callbacks.quotes import quotes_panel
        quotes_panel(call)
    
    # ==========================================
    # ДИАЛОГ С АГЕНТОМ
    # ==========================================
    @bot.callback_query_handler(func=lambda call: call.data == "start_dialog")
    def start_dialog(call):
        from dialogue.admin_commands import show_dialog_ui
        show_dialog_ui(call, bot)
    
    # ==========================================
    # ВЫХОД ИЗ АДМИНКИ
    # ==========================================
    @bot.callback_query_handler(func=lambda call: call.data == "admin_logout")
    def admin_logout(call):
        from dialogue.admin_commands import logout_admin
        user_id = call.from_user.id
        logout_admin(user_id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.answer_callback_query(call.id, "👋 Вы вышли из админ-панели")
