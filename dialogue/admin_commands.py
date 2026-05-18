# ==========================================
# Модуль: dialogue/admin_commands.py
# Справка: README.md → Админка
# Задача: админ-меню, управление режимами, цитатами, постами
# Комментарий: кнопка "🎬 Пост в VK (с медиа)" использует add_publication
# ==========================================

import os
import json
import time
import tempfile
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.ping_modes import apply_ping_mode
from dialogue.publisher import add_publication, load_publications
from dialogue.publisher_utils import get_auto_tags, get_random_quote

CONFIG_FILE = "config.json"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))

MODES = ["утро", "день", "вечер", "ночь"]

GREETINGS = {
    "утро": "🌅 Доброе утро, сапёр. Сеть тлеет, ритм 0,8 Гц стабилен.",
    "день": "☀️ Хорошего дня. Не забывай #Тлеем.",
    "вечер": "🌙 Спокойного вечера. Наблюдение продолжается.",
    "ночь": "😴 Режим сна. Старший брат отдыхает. Вопросы — утром."
}

# Хранилище активных сессий админа
admin_sessions = {}
SESSION_TIMEOUT = 1800  # 30 минут

# Блокировка после 3 попыток
failed_attempts = {}
BLOCK_TIME = 3600  # 1 час
MAX_ATTEMPTS = 3

def is_blocked(user_id):
    if user_id in failed_attempts:
        attempts, block_until = failed_attempts[user_id]
        if time.time() < block_until:
            return True
        else:
            del failed_attempts[user_id]
    return False

def register_failed_attempt(user_id, bot):
    attempts, block_until = failed_attempts.get(user_id, (0, 0))
    attempts += 1
    
    if attempts >= MAX_ATTEMPTS:
        block_until = time.time() + BLOCK_TIME
        try:
            bot.send_message(
                ADMIN_USER_ID,
                f"⚠️ *Попытка взлома админки!*\n\n"
                f"User ID: `{user_id}`\n"
                f"Заблокирован на 1 час.\n"
                f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='Markdown'
            )
        except:
            pass
        print(f"[ADMIN] Блокировка user_id {user_id} на 1 час")
    
    failed_attempts[user_id] = (attempts, block_until)

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
    
    keyboard.add(InlineKeyboardButton("🤖 Управление ботом", callback_data="noop"))
    keyboard.add(
        InlineKeyboardButton("🌅 Утро", callback_data="mode_утро"),
        InlineKeyboardButton("☀️ День", callback_data="mode_день"),
        InlineKeyboardButton("🌙 Вечер", callback_data="mode_вечер"),
        InlineKeyboardButton("😴 Ночь", callback_data="mode_ночь"),
        InlineKeyboardButton("⏱ Пинг 30", callback_data="ping_30"),
        InlineKeyboardButton("⏱ Пинг 60", callback_data="ping_60"),
        InlineKeyboardButton("⏱ Пинг 180", callback_data="ping_180")
    )
    
    config = load_config()
    alisa_enabled = config.get("alisa", {}).get("enabled", True)
    alisa_status = "✅" if alisa_enabled else "❌"
    keyboard.add(InlineKeyboardButton(f"🤖 Старший брат {alisa_status}", callback_data="toggle_alisa"))
    
    keyboard.add(InlineKeyboardButton("📝 Управление контентом", callback_data="noop"))
    keyboard.add(
        InlineKeyboardButton("📤 Публикации", callback_data="pub_menu"),
        InlineKeyboardButton("➕ Добавить пост", callback_data="add_post"),
        InlineKeyboardButton("🎬 Пост в VK (с медиа)", callback_data="vk_post")
    )
    
    keyboard.add(InlineKeyboardButton("📜 Управление цитатами", callback_data="noop"))
    keyboard.add(
        InlineKeyboardButton("📋 Список цитат", callback_data="quotes_list"),
        InlineKeyboardButton("➕ Добавить цитату", callback_data="quotes_add"),
        InlineKeyboardButton("⏱ Интервал цитат", callback_data="quotes_interval")
    )
    
    keyboard.add(InlineKeyboardButton("🔧 Диагностика", callback_data="noop"))
    keyboard.add(
        InlineKeyboardButton("📋 Ошибки", callback_data="errors"),
        InlineKeyboardButton("📜 Лог", callback_data="log")
    )
    
    keyboard.add(InlineKeyboardButton("🚪 Выйти", callback_data="logout"))
    
    return keyboard

def get_user_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💥 #Тлеем", callback_data="tleem"),
        InlineKeyboardButton("🔒 #Фиксируем", callback_data="fixiruem"),
        InlineKeyboardButton("⚡ #Вспышка", callback_data="vspishka"),
        InlineKeyboardButton("🌬 #дышим", callback_data="dyshim"),
        InlineKeyboardButton("🗣 #говорим", callback_data="govorim"),
        InlineKeyboardButton("📖 #справка", callback_data="help")
    )
    return keyboard

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

def handle_callback_mode(mode, bot, chat_id, message_id, user_id):
    config = load_config()
    config["force_mode"] = mode
    config["force_mode_until"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_config(config)
    apply_ping_mode()
    log_admin_action(user_id, f"mode {mode}", "success")
    bot.edit_message_text(
        f"✅ Режим «{mode}» установлен сейчас\n\n{GREETINGS.get(mode, '')}",
        chat_id, message_id
    )
    return_to_admin_menu(bot, chat_id, message_id, user_id)

def handle_callback_ping(interval, bot, chat_id, message_id, user_id):
    config = load_config()
    if "ping" not in config:
        config["ping"] = {}
    config["ping"]["interval"] = interval
    save_config(config)
    apply_ping_mode()
    log_admin_action(user_id, f"ping {interval}", "success")
    bot.edit_message_text(f"✅ Пинг установлен на {interval} секунд", chat_id, message_id)
    return_to_admin_menu(bot, chat_id, message_id, user_id)

def handle_callback_errors(user_id, bot, chat_id, message_id):
    if os.path.exists("error.log"):
        with open("error.log", "r", encoding="utf-8") as f:
            errors = f.read().strip()
        if errors:
            for i in range(0, len(errors), 4000):
                bot.send_message(user_id, f"```\n{errors[i:i+4000]}\n```", parse_mode='Markdown')
            bot.edit_message_text("✅ Ошибки отправлены в личку", chat_id, message_id)
        else:
            bot.edit_message_text("📭 Ошибок нет", chat_id, message_id)
    else:
        bot.edit_message_text("📭 Файл error.log не найден", chat_id, message_id)
    return_to_admin_menu(bot, chat_id, message_id, user_id)

def handle_callback_log(user_id, bot, chat_id, message_id):
    if os.path.exists("admin.log"):
        with open("admin.log", "r", encoding="utf-8") as f:
            log_data = f.read().strip()
        if log_data:
            for i in range(0, len(log_data), 4000):
                bot.send_message(user_id, f"```log\n{log_data[i:i+4000]}\n```", parse_mode='Markdown')
            bot.edit_message_text("✅ Лог отправлен в личку", chat_id, message_id)
        else:
            bot.edit_message_text("📭 Лог пуст", chat_id, message_id)
    else:
        bot.edit_message_text("📭 Файл admin.log не найден", chat_id, message_id)
    return_to_admin_menu(bot, chat_id, message_id, user_id)

def handle_callback_logout(user_id, bot, chat_id, message_id):
    logout_admin(user_id)
    log_admin_action(user_id, "logout", "success")
    bot.edit_message_text("🔓 Вы вышли из админ-панели", chat_id, message_id)

def handle_callback_pub_menu(bot, chat_id, message_id, user_id):
    pubs = load_publications()
    if not pubs:
        bot.edit_message_text("📭 Нет отложенных публикаций", chat_id, message_id)
    else:
        text = "📋 *Отложенные публикации:*\n\n"
        for p in pubs:
            status = "✅" if p["status"] == "published" else "⏳"
            text += f"{status} `{p['text'][:50] if p['text'] else '[Без текста]'}...` ({p['chat_id']})\n"
        bot.edit_message_text(text, chat_id, message_id, parse_mode='Markdown')
    return_to_admin_menu(bot, chat_id, message_id, user_id)

def handle_callback_toggle_alisa(bot, chat_id, message_id, user_id):
    config = load_config()
    if "alisa" not in config:
        config["alisa"] = {}
    config["alisa"]["enabled"] = not config["alisa"].get("enabled", True)
    save_config(config)
    status = "включён" if config["alisa"]["enabled"] else "выключен"
    log_admin_action(user_id, "toggle_alisa", status)
    bot.edit_message_text(f"🤖 Старший брат {status}", chat_id, message_id)
    return_to_admin_menu(bot, chat_id, message_id, user_id)

def handle_callback_quotes_list(bot, chat_id, message_id, user_id):
    from dialogue.quotes import get_quotes_list
    quotes = get_quotes_list()
    if not quotes:
        bot.edit_message_text("📭 Список цитат пуст", chat_id, message_id)
    else:
        text = "📜 *Список цитат:*\n\n"
        for i, q in enumerate(quotes):
            text += f"`{i+1}.` {q[:60]}{'...' if len(q) > 60 else ''}\n"
            if len(text) > 3500:
                bot.send_message(user_id, text, parse_mode='Markdown')
                text = ""
        if text:
            bot.edit_message_text(text, chat_id, message_id, parse_mode='Markdown')
    return_to_admin_menu(bot, chat_id, message_id, user_id)

def handle_callback_quotes_add_start(bot, chat_id, message_id, user_id):
    msg = bot.send_message(chat_id, "✍️ Введите текст новой цитаты:")
    bot.register_next_step_handler(msg, process_quote_add, bot, chat_id, user_id)

def process_quote_add(message, bot, chat_id, user_id):
    text = message.text.strip()
    if not text:
        bot.send_message(chat_id, "❌ Цитата не может быть пустой")
    else:
        from dialogue.quotes import add_quote
        add_quote(text)
        log_admin_action(user_id, f"add_quote: {text[:50]}", "success")
        bot.send_message(chat_id, f"✅ Цитата добавлена:\n\n{text}")
    return_to_admin_menu(bot, chat_id, user_id=user_id)

def handle_callback_quotes_interval(bot, chat_id, message_id, user_id):
    from dialogue.quotes import get_quotes_interval_minutes
    current = get_quotes_interval_minutes()
    keyboard = InlineKeyboardMarkup(row_width=3)
    for minutes in [15, 30, 60, 120, 240, 480]:
        marker = "✅" if minutes == current else ""
        keyboard.add(InlineKeyboardButton(f"{minutes} мин {marker}", callback_data=f"quote_int_{minutes}"))
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="admin_menu"))
    bot.edit_message_text(
        f"⏱ *Интервал публикации цитат*\n\nТекущий: {current} минут\n\nВыбери новый:",
        chat_id, message_id, parse_mode='Markdown', reply_markup=keyboard
    )

def handle_callback_quotes_set_interval(interval, bot, chat_id, message_id, user_id):
    from dialogue.quotes import set_quotes_interval_minutes, quotes_loop, load_config as load_cfg
    set_quotes_interval_minutes(interval)
    import dialogue.quotes as quotes_module
    quotes_module.quote_thread_running = False
    time.sleep(1)
    cfg = load_cfg()
    TG_CHAT_ID = cfg.get("telegram", {}).get("publish_channel", "@qwestomir")
    quotes_module.quotes_loop(bot, TG_CHAT_ID)
    log_admin_action(user_id, f"quotes_interval {interval}", "success")
    bot.edit_message_text(f"✅ Интервал цитат установлен: {interval} минут", chat_id, message_id)
    return_to_admin_menu(bot, chat_id, message_id, user_id)

# ==========================================
# Блок: мгновенный пост в VK (через публикатор)
# ==========================================

def handle_callback_vk_post(bot, chat_id, message_id, user_id):
    msg = bot.send_message(chat_id, "✍️ Введите текст поста для VK (можно с хештегами):")
    bot.register_next_step_handler(msg, process_vk_post_text, bot, chat_id, user_id)

def process_vk_post_text(message, bot, chat_id, user_id):
    text = message.text.strip()
    if not text:
        bot.send_message(chat_id, "❌ Текст не может быть пустым")
        return_to_admin_menu(bot, chat_id, user_id=user_id)
        return
    msg = bot.send_message(chat_id, "📎 Пришлите фото, видео или нажмите /skip")
    bot.register_next_step_handler(msg, process_vk_post_file, bot, chat_id, text, user_id)

def process_vk_post_file(message, bot, chat_id, text, user_id):
    file_path = None
    if message.text and message.text.lower() == "/skip":
        file_path = None
    elif message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        # Сохраняем во временную папку /tmp (Render разрешает запись)
        file_path = os.path.join(tempfile.gettempdir(), f"temp_vk_{message.photo[-1].file_id}.jpg")
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        print(f"[DEBUG] Фото сохранено: {file_path}, размер: {os.path.getsize(file_path)} байт")
    elif message.video:
        file_info = bot.get_file(message.video.file_id)
        file_path = os.path.join(tempfile.gettempdir(), f"temp_vk_{message.video.file_id}.mp4")
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        print(f"[DEBUG] Видео сохранено: {file_path}")
    elif message.document:
        ext = os.path.splitext(message.document.file_name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi']:
            file_info = bot.get_file(message.document.file_id)
            file_path = os.path.join(tempfile.gettempdir(), f"temp_vk_{message.document.file_id}_{message.document.file_name}")
            downloaded_file = bot.download_file(file_info.file_path)
            with open(file_path, 'wb') as f:
                f.write(downloaded_file)
            print(f"[DEBUG] Документ сохранён: {file_path}")
        else:
            bot.send_message(chat_id, "❌ Неподдерживаемый тип файла. Пост будет без вложения.")
    else:
        bot.send_message(chat_id, "❌ Неподдерживаемый тип медиа. Пост будет без вложения.")
    
    config = load_config()
    vk_token = os.environ.get("VK_TOKEN") or config.get("vk", {}).get("token")
    vk_owner_id = os.environ.get("VK_OWNER_ID") or config.get("vk", {}).get("owner_id")
    
    if not vk_token or not vk_owner_id:
        bot.send_message(chat_id, "❌ Нет токена VK. Проверь переменные окружения.")
        return_to_admin_menu(bot, chat_id, user_id=user_id)
        return
    
    quote = get_random_quote()
    full_text = f"{text}\n\n📜 {quote}"
    auto_tags = get_auto_tags(text, "vk")
    
    # Добавляем публикацию с задержкой 0
    add_publication("vk", full_text, 0, auto_tags, file_path)
    
    bot.send_message(chat_id, f"✅ Пост отправлен в VK:\n\n{full_text[:200]}")
    
    # Удаляем временный файл
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        print(f"[DEBUG] Временный файл удалён: {file_path}")
    
    return_to_admin_menu(bot, chat_id, user_id=user_id)

# ==========================================
# Отложенные публикации (старая логика)
# ==========================================

def ask_for_post_text(bot, chat_id, message_id):
    msg = bot.send_message(chat_id, "✍️ Введите текст поста (можно с Markdown) или /skip для поста без текста")
    bot.register_next_step_handler(msg, process_post_text, bot, chat_id)

def process_post_text(message, bot, chat_id):
    text = None
    if message.text != "/skip":
        text = message.text
    ask_for_post_file(bot, chat_id, text)

def ask_for_post_file(bot, chat_id, text):
    msg = bot.send_message(chat_id, "📎 Пришлите файл (фото, видео, документ) или нажмите /skip")
    bot.register_next_step_handler(msg, process_post_file, bot, chat_id, text)

def process_post_file(message, bot, chat_id, text):
    file_path = None
    if message.text == "/skip":
        file_path = None
    elif message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_path = os.path.join(tempfile.gettempdir(), f"temp_{message.photo[-1].file_id}.jpg")
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
    elif message.document:
        file_info = bot.get_file(message.document.file_id)
        file_path = os.path.join(tempfile.gettempdir(), f"temp_{message.document.file_id}_{message.document.file_name}")
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
    elif message.video:
        file_info = bot.get_file(message.video.file_id)
        file_path = os.path.join(tempfile.gettempdir(), f"temp_{message.video.file_id}.mp4")
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
    else:
        bot.send_message(chat_id, "❌ Неподдерживаемый тип файла. Пост будет без вложения.")
    
    ask_for_post_delay(bot, chat_id, text, file_path)

def ask_for_post_delay(bot, chat_id, text, file_path):
    msg = bot.send_message(chat_id, "⏱ Через сколько минут опубликовать? (число)")
    bot.register_next_step_handler(msg, process_post_delay, bot, chat_id, text, file_path)

def process_post_delay(message, bot, chat_id, text, file_path):
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
    default_tags = pub_config.get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")
    
    add_publication("telegram", text, delay_seconds, default_tags, file_path)
    user_id = message.from_user.id
    log_admin_action(user_id, f"add_post in {delay_minutes} min, text: {bool(text)}, file: {bool(file_path)}", "success")
    bot.send_message(chat_id, f"✅ Пост запланирован через {delay_minutes} минут")
    return_to_admin_menu(bot, chat_id, user_id=user_id)

# ==========================================
# Обработчик команды #админ
# ==========================================

def handle_admin_command(message, bot):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass
    
    if is_blocked(user_id):
        bot.send_message(chat_id, "❌ Доступ заблокирован на 1 час из-за слишком частых неудачных попыток.")
        return
    
    if user_id != ADMIN_USER_ID:
        register_failed_attempt(user_id, bot)
        try:
            bot.send_message(
                user_id,
                "❌ Неверный пароль. Доступ запрещён.\n\n"
                "Попробуйте позже или обратитесь к администратору.",
                parse_mode='Markdown'
            )
        except:
            pass
        return

    parts = message.text.split()
    if len(parts) == 2 and parts[1] == ADMIN_PASSWORD:
        authorize_admin(user_id, parts[1])
        log_admin_action(user_id, "login", "success")
        failed_attempts.pop(user_id, None)
        bot.send_message(chat_id, "✅ Авторизован. Ваше меню:", reply_markup=get_admin_menu())
    else:
        register_failed_attempt(user_id, bot)
        try:
            bot.send_message(
                user_id,
                "❌ Неверный пароль. Доступ запрещён.\n\n"
                "Попробуйте позже или обратитесь к администратору.",
                parse_mode='Markdown'
            )
        except:
            pass
