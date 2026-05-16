import os
import json
import time
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.ping_modes import apply_ping_mode
from dialogue.publisher import add_publication, load_publications

CONFIG_FILE = "config.json"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))

MODES = ["утро", "день", "вечер", "сон"]

GREETINGS = {
    "утро": "🌅 Доброе утро, сапёр. Сеть тлеет, ритм 0,8 Гц стабилен.",
    "день": "☀️ Хорошего дня. Не забывай #Тлеем.",
    "вечер": "🌙 Спокойного вечера. Наблюдение продолжается.",
    "сон": "😴 Режим сна. Старший брат отдыхает. Вопросы — утром."
}

# Хранилище активных сессий админа
admin_sessions = {}
SESSION_TIMEOUT = 1800  # 30 минут

def is_admin_authorized(user_id):
    if user_id != ADMIN_USER_ID:
        return False
    if user_id in admin_sessions:
        if time.time() - admin_sessions[user_id] < SESSION_TIMEOUT:
            return True
    return False

def authorize_admin(user_id, password):
    if user_id == ADMIN_USER_ID and password == ADMIN_PASSWORD:
        admin_sessions[user_id] = time.time()
        return True
    return False

def logout_admin(user_id):
    admin_sessions.pop(user_id, None)

def log_admin_action(user_id, action, result):
    with open("admin.log", "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} | user:{user_id} | {action} | {result}\n")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get_admin_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🌅 Утро", callback_data="mode_утро"),
        InlineKeyboardButton("☀️ День", callback_data="mode_день"),
        InlineKeyboardButton("🌙 Вечер", callback_data="mode_вечер"),
        InlineKeyboardButton("😴 Сон", callback_data="mode_сон"),
        InlineKeyboardButton("⏱ Пинг 30", callback_data="ping_30"),
        InlineKeyboardButton("⏱ Пинг 60", callback_data="ping_60"),
        InlineKeyboardButton("⏱ Пинг 180", callback_data="ping_180"),
        InlineKeyboardButton("📋 Ошибки", callback_data="errors"),
        InlineKeyboardButton("📜 Лог", callback_data="log"),
        InlineKeyboardButton("📤 Публикации", callback_data="pub_menu"),
        InlineKeyboardButton("➕ Добавить пост", callback_data="add_post"),
        InlineKeyboardButton("❌ Выйти", callback_data="logout")
    )
    return keyboard

def get_user_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💥 #Тлеем", callback_data="tleem"),
        InlineKeyboardButton("🔒 #Фиксируем", callback_data="fixiruem"),
        InlineKeyboardButton("⚡ #Вспышка", callback_data="vspishka"),
        InlineKeyboardButton("🌬 #дышим", callback_data="dyshim"),
        InlineKeyboardButton("🗣 #говорим", callback_data="govorim"),
        InlineKeyboardButton("📖 #помощь", callback_data="help")
    )
    return keyboard

def handle_callback_mode(mode, bot, chat_id, message_id, user_id):
    config = load_config()
    if "force_mode" not in config:
        config["force_mode"] = {}
    config["force_mode"] = mode
    config["force_mode_until"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_config(config)
    apply_ping_mode()
    log_admin_action(user_id, f"mode {mode}", "success")
    bot.edit_message_text(
        f"✅ Режим «{mode}» установлен сейчас\n\n{GREETINGS.get(mode, '')}",
        chat_id, message_id
    )

def handle_callback_ping(interval, bot, chat_id, message_id, user_id):
    config = load_config()
    if "ping" not in config:
        config["ping"] = {}
    config["ping"]["interval"] = interval
    save_config(config)
    apply_ping_mode()
    log_admin_action(user_id, f"ping {interval}", "success")
    bot.edit_message_text(f"✅ Пинг установлен на {interval} секунд", chat_id, message_id)

def handle_callback_errors(user_id, bot, chat_id, message_id):
    if os.path.exists("error.log"):
        with open("error.log", "r", encoding="utf-8") as f:
            errors = f.read().strip()
        if errors:
            for i in range(0, len(errors), 4000):
                bot.send_message(user_id, errors[i:i+4000])
            bot.edit_message_text("✅ Ошибки отправлены в личку", chat_id, message_id)
        else:
            bot.edit_message_text("📭 Ошибок нет", chat_id, message_id)
    else:
        bot.edit_message_text("📭 Файл error.log не найден", chat_id, message_id)

def handle_callback_log(user_id, bot, chat_id, message_id):
    if os.path.exists("admin.log"):
        with open("admin.log", "r", encoding="utf-8") as f:
            log_data = f.read().strip()
        if log_data:
            for i in range(0, len(log_data), 4000):
                bot.send_message(user_id, log_data[i:i+4000])
            bot.edit_message_text("✅ Лог отправлен в личку", chat_id, message_id)
        else:
            bot.edit_message_text("📭 Лог пуст", chat_id, message_id)
    else:
        bot.edit_message_text("📭 Файл admin.log не найден", chat_id, message_id)

def handle_callback_logout(user_id, bot, chat_id, message_id):
    logout_admin(user_id)
    log_admin_action(user_id, "logout", "success")
    bot.edit_message_text("🔓 Вы вышли из админ-панели", chat_id, message_id)

def handle_callback_pub_menu(bot, chat_id, message_id, user_id):
    pubs = load_publications()
    if not pubs:
        bot.edit_message_text("📭 Нет отложенных публикаций", chat_id, message_id)
        return
    text = "📋 *Отложенные публикации:*\n\n"
    for p in pubs:
        status = "✅" if p["status"] == "published" else "⏳"
        text += f"{status} `{p['text'][:50]}...` ({p['chat_id']})\n"
    bot.edit_message_text(text, chat_id, message_id, parse_mode='Markdown')

def ask_for_post_text(bot, chat_id, message_id):
    msg = bot.send_message(chat_id, "✍️ Введите текст поста (можно с Markdown):")
    bot.register_next_step_handler(msg, process_post_text, bot, chat_id)

def process_post_text(message, bot, chat_id):
    text = message.text
    if not text:
        bot.send_message(chat_id, "❌ Текст не может быть пустым")
        return
    ask_for_post_delay(bot, chat_id, text)

def ask_for_post_delay(bot, chat_id, text):
    msg = bot.send_message(chat_id, "⏱ Через сколько минут опубликовать? (число)")
    bot.register_next_step_handler(msg, process_post_delay, bot, chat_id, text)

def process_post_delay(message, bot, chat_id, text):
    try:
        delay_minutes = int(message.text.strip())
        if delay_minutes <= 0:
            raise ValueError
    except:
        bot.send_message(chat_id, "❌ Введите положительное число минут")
        return
    delay_seconds = delay_minutes * 60
    config = load_config()
    pub_config = config.get("publisher", {})
    default_tags = pub_config.get("default_tags", "#СапёрыАутентичности")
    
    add_publication("telegram", text, delay_seconds, default_tags)
    user_id = message.from_user.id
    log_admin_action(user_id, f"add_post in {delay_minutes} min", "success")
    bot.send_message(chat_id, f"✅ Пост запланирован через {delay_minutes} минут")

def handle_admin_command(message, bot):
    user_id = message.from_user.id
    if user_id != ADMIN_USER_ID:
        bot.reply_to(message, "❌ Доступ запрещён.")
        return

    parts = message.text.split()
    if len(parts) == 2 and parts[1] == ADMIN_PASSWORD:
        authorize_admin(user_id, parts[1])
        log_admin_action(user_id, "login", "success")
        bot.reply_to(message, "✅ Авторизован. Ваше меню:", reply_markup=get_admin_menu())
    else:
        bot.reply_to(message, "❌ Неверный пароль. Попробуйте: #админ <пароль>")
