# ==========================================
# Файл: dialogue/admin_commands.py
# Справка: README.md → Админ-панель
# Задача: команда #админ, авторизация, вызов меню, диалог
# Комментарий: добавление поста — без режима ожидания (скрепка доступна)
# ==========================================

import os
import threading
import time
from debug_utils import debug_log
from dialogue.button_map import get_admin_menu_keyboard
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.state_manager import user_states

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "tleem2026")

authorized_admins = {}

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
    
    bot.reply_to(message, f"🔐 Введите пароль:\n`#админ {ADMIN_PASSWORD}`", parse_mode='Markdown')

# ==========================================
# ДОБАВЛЕНИЕ ПОСТА (без режима ожидания, скрепка доступна)
# ==========================================

def show_add_post_ui(call, bot):
    user_id = call.from_user.id
    # Удаляем меню, чтобы не висело
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    # Отправляем обычное сообщение (не в режиме ожидания)
    bot.send_message(
        call.message.chat.id,
        "📝 *Добавление поста*\n\n"
        "Просто отправьте фото или видео с подписью (текстом).\n"
        "Теги пишите прямо в подписи.\n"
        "Для отмены введите /cancel",
        parse_mode='Markdown'
    )
    
    # Устанавливаем состояние, чтобы бот понял, что это пост
    user_states[user_id] = "waiting_simple_post"
    bot.answer_callback_query(call.id)

def cancel_add_post(call, bot):
    user_id = call.from_user.id
    user_states.pop(user_id, None)
    bot.edit_message_text(
        "❌ *Добавление поста отменено.*",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

# ==========================================
# ДИАЛОГ С АГЕНТОМ
# ==========================================

def show_dialog_ui(call, bot):
    user_id = call.from_user.id
    user_states[user_id] = "waiting_dialog"
    bot.edit_message_text(
        "🗣 *Диалог с агентом*\n\n"
        "Просто напишите сообщение.\n"
        "/cancel — отменить диалог",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)
