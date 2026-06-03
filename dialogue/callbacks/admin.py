# ==========================================
# Файл: dialogue/callbacks/admin.py
# Справка: README.md → Обработчики кнопок / Админ
# Задача: обработка кнопок админ-меню (только главное меню)
# Комментарий: вынесены цитаты (quotes.py) и диалог (dialog.py)
# Зависит от: telebot, button_map, admin_commands
# Вызывается из: dialogue/callbacks/__init__.py
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

def show_admin_panel(call):
    """Показывает главное админ-меню (может вызываться из других модулей)"""
    from dialogue.callbacks import bot as global_bot
    global_bot.edit_message_text(
        "🛡️ *Админ-панель*\n\nВыберите действие:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=get_admin_menu_keyboard(),
        parse_mode='Markdown'
    )
    auto_delete_menu(global_bot, call.message.chat.id, call.message.message_id)
    global_bot.answer_callback_query(call.id)

def register_admin_callbacks(bot, config):
    # Сохраняем bot для использования в show_admin_panel
    import dialogue.callbacks as cb
    cb.bot = bot
    
    @bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
    def admin_panel(call):
        show_admin_panel(call)
    
    @bot.callback_query_handler(func=lambda call: call.data == "add_post")
    def add_post_ui(call):
        from dialogue.admin_commands import show_add_post_ui
        show_add_post_ui(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == "cancel_add_post")
    def cancel_post(call):
        from dialogue.admin_commands import cancel_add_post
        cancel_add_post(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == "start_dialog")
    def start_dialog(call):
        from dialogue.admin_commands import show_dialog_ui
        show_dialog_ui(call, bot)
    
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
