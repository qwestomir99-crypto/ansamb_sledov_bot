# ==========================================
# Модуль: dialogue/admin_commands.py
# Справка: README.md → Админка (диспетчер)
# Задача: обработка команды #админ, импорт всех админ-функций
# Комментарий: рефакторинг — всё перенесено в dialogue/admin/
# ==========================================

import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.admin import (
    get_admin_menu,
    get_user_menu,
    is_admin_authorized,
    authorize_admin,
    logout_admin,
    is_blocked,
    register_failed_attempt,
    log_admin_action,
    handle_quotes_list,
    handle_quotes_add_start,
    handle_quotes_interval,
    handle_quotes_set_interval,
    handle_pub_menu,
    ask_for_post_text,
    handle_vk_post,
    handle_errors,
    handle_log,
    handle_debug,
    handle_callback_mode,
    handle_callback_ping,
    handle_callback_toggle_alisa
)
from dialogue.publisher import add_publication, load_publications
from dialogue.publisher_utils import get_auto_tags, get_random_quote, post_to_vk
from dialogue.quotes import get_quotes_list, add_quote, get_quotes_interval_minutes, set_quotes_interval_minutes, quotes_loop, load_config as load_cfg
from dialogue.ping_modes import apply_ping_mode

CONFIG_FILE = "config.json"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def return_to_admin_menu(bot, chat_id, message_id=None, user_id=None):
    if user_id and not is_admin_authorized(user_id):
        return
    if message_id:
        bot.edit_message_text(
            "🛡️ Админ-меню:",
            chat_id, message_id,
            reply_markup=get_admin_menu()
        )
    else:
        bot.send_message(chat_id, "🛡️ Админ-меню:", reply_markup=get_admin_menu())

# ------------------------------------------------------------
# Обработчик команды #админ (полный)
# ------------------------------------------------------------

def handle_admin_command(message, bot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if is_blocked(user_id):
        bot.send_message(chat_id, "❌ Доступ заблокирован на 1 час.")
        return
    
    if is_admin_authorized(user_id):
        bot.send_message(chat_id, "🛡️ Админ-меню:", reply_markup=get_admin_menu())
        return
    
    parts = message.text.split()
    if len(parts) == 2 and len(parts[1]) > 3:
        password = parts[1]
        if password == ADMIN_PASSWORD:
            authorize_admin(user_id, password)
            log_admin_action(user_id, "login", "success")
            failed_attempts.pop(user_id, None)
            bot.send_message(chat_id, "✅ Авторизован. Ваше меню:", reply_markup=get_admin_menu())
        else:
            register_failed_attempt(user_id, bot)
            bot.send_message(chat_id, "❌ Неверный пароль.")
        try:
            bot.delete_message(chat_id, message.message_id)
        except:
            pass
        return
    
    msg = bot.send_message(chat_id, "🔐 Введите пароль для входа в админ-панель:")
    bot.register_next_step_handler(msg, process_admin_password, bot, user_id, chat_id)
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass

def process_admin_password(message, bot, user_id, chat_id):
    password = message.text.strip()
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    if password == ADMIN_PASSWORD:
        authorize_admin(user_id, password)
        log_admin_action(user_id, "login", "success")
        failed_attempts.pop(user_id, None)
        bot.send_message(chat_id, "✅ Авторизован. Ваше меню:", reply_markup=get_admin_menu())
    else:
        register_failed_attempt(user_id, bot)
        bot.send_message(chat_id, "❌ Неверный пароль. Доступ запрещён.")
