# ==========================================
# Файл: dialogue/admin_commands.py
# Справка: README.md → Админ-панель
# Задача: команда #админ, авторизация, вызов меню, добавление поста
# ==========================================

import os
import threading
import time
from debug_utils import debug_log
from dialogue.button_map import get_admin_menu_keyboard

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "tleem2026")

authorized_admins = {}
user_states = {}  # свой словарь вместо импорта из message_dispatcher

def is_admin_authorized(user_id):
    return authorized_admins.get(user_id, False)

def authorize_admin(user_id, password):
    if password == ADMIN_PASSWORD:
        authorized_admins[user_id] = True
        debug_log("ADMIN", f"Админ {user_id} авторизован")
        return True
    return False

def logout_admin(user_id):
    if user_id in authorized_admins:
        del authorized_admins[user_id]
        debug_log("ADMIN", f"Админ {user_id} вышел")

def safe_delete(bot, message, delay=3):
    def _delete():
        time.sleep(delay)
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
    threading.Thread(target=_delete, daemon=True).start()

def handle_admin_command(message, bot):
    user_id = message.from_user.id
    text = message.text.lower()
    
    if is_admin_authorized(user_id):
        bot.reply_to(message, "🛡️ Админ-меню:", reply_markup=get_admin_menu_keyboard())
        safe_delete(bot, message, 3)
        return
    
    parts = text.split(maxsplit=1)
    if len(parts) > 1:
        password = parts[1]
        if authorize_admin(user_id, password):
            bot.reply_to(message, "✅ Авторизация успешна!", reply_markup=get_admin_menu_keyboard())
            safe_delete(bot, message, 3)
        else:
            msg = bot.reply_to(message, "❌ Неверный пароль.")
            safe_delete(bot, message, 3)
            safe_delete(bot, msg, 5)
        return
    
    bot.reply_to(message, "🔐 Введите пароль для входа в админ-панель:\n(или #админ пароль)")

# ==========================================
# ДОБАВЛЕНИЕ ПОСТА
# ==========================================

def show_add_post_ui(call, bot):
    user_id = call.from_user.id
    user_states[user_id] = "waiting_for_post"
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    bot.send_message(
        call.message.chat.id,
        "📝 *Добавление поста*\n\n"
        "Пришлите текст поста (можно с фото/видео).\n"
        "Для отмены введите /cancel",
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)
