# ==========================================
# Файл: dialogue/admin_commands.py
# Справка: README.md → Админ-панель
# Задача: авторизация, главное меню, вызов модулей
# Комментарий: посты → admin/posts.py, цитаты → admin/quotes_admin.py
# ==========================================

import os
import json
import threading
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from dialogue.button_map import (
    get_admin_menu_keyboard, get_user_menu_keyboard, 
    get_text, get_callback, get_moods_keyboard, get_dialog_keyboard
)
from debug_utils import debug_log

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "tleem2026")

def safe_delete(message, delay=3):
    def _delete():
        time.sleep(delay)
        try:
            bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
    threading.Thread(target=_delete, daemon=True).start()

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

def get_admin_menu():
    return get_admin_menu_keyboard()

def get_user_menu():
    return get_user_menu_keyboard()

def handle_admin_command(message, bot):
    user_id = message.from_user.id
    text = message.text.lower()
    if is_admin_authorized(user_id):
        bot.reply_to(message, "🛡️ Админ-меню:", reply_markup=get_admin_menu())
        safe_delete(message, 3)
        return
    parts = text.split(maxsplit=1)
    if len(parts) > 1:
        if authorize_admin(user_id, parts[1]):
            bot.reply_to(message, "✅ Авторизация успешна!", reply_markup=get_admin_menu())
            safe_delete(message, 3)
        else:
            msg = bot.reply_to(message, "❌ Неверный пароль.")
            safe_delete(message, 3)
            safe_delete(msg, 5)
        return
    bot.reply_to(message, "🔐 Введите пароль:\n(или #админ пароль)")

def show_admin_panel(call, bot):
    bot.edit_message_text("🛡️ *Админ-панель*\n\nВыберите действие:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_admin_menu(), parse_mode='Markdown')
    bot.answer_callback_query(call.id)

# ==========================================
# ДИАГНОСТИКА, ВЫХОД, НАСТРОЕНИЕ, ДИАЛОГ
# ==========================================
def show_diagnostics(call, bot):
    from dialogue.admin.diagnostics import get_diagnostics_menu
    bot.edit_message_text("📋 *Диагностика*", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_diagnostics_menu(), parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def admin_logout(call, bot):
    logout_admin(call.from_user.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    msg = bot.send_message(call.message.chat.id, "👋 Вы вышли.")
    safe_delete(msg, 3)
    bot.answer_callback_query(call.id)

def show_mood_menu(call, bot):
    bot.edit_message_text("🎭 *Настроение*", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_moods_keyboard(with_back=True), parse_mode='Markdown')
    bot.answer_callback_query(call.id)

def show_dialog_ui(call, bot):
    msg = bot.send_message(call.message.chat.id, "🗣 Напишите сообщение.", parse_mode='Markdown')
    safe_delete(call.message, 1)
    bot.register_next_step_handler(msg, process_dialog_message, bot)

def process_dialog_message(message, bot):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Отменён.")
        safe_delete(message, 3)
        return
    from dialogue.agent import ask_agent
    status_msg = bot.reply_to(message, "⏳ Думаю...")
    answer = ask_agent(message.text, user_id=message.from_user.id)
    try:
        bot.delete_message(status_msg.chat.id, status_msg.message_id)
    except:
        pass
    bot.reply_to(message, f"🗣 {answer}" if answer else "🌙 Отдыхает.")
    safe_delete(message, 5)
