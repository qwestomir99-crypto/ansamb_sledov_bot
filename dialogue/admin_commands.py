# ==========================================
# Файл: dialogue/admin_commands.py
# Справка: README.md → Админ-панель
# Задача: админ-меню, кнопки, управление цитатами, постинг в VK
# Комментарий: использует button_map.py для единого управления кнопками
#              Добавлено подменю «Настроение» и кнопка диалога
#              Добавлено автоудаление сообщений (safe_delete)
# Зависит от: telebot, button_map, publisher, quotes, diagnostics
# Вызывается из: bot.py (handle_message), callbacks.py
# ==========================================

import os
import random
import json
import threading
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================================
# ИМПОРТ МОДУЛЕЙ ПРОЕКТА
# ==========================================
from dialogue.button_map import get_admin_menu_keyboard, get_user_menu_keyboard, get_text, get_callback
from dialogue.publisher import add_publication
from dialogue.quotes import get_quotes_list, add_quote, set_quotes_interval, get_quotes_interval
from debug_utils import debug_log
from ping_utils import ping_self

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "tleem2026")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (удаление портянки)
# ==========================================
def safe_delete(message, delay=3):
    """Безопасно удаляет сообщение с задержкой"""
    def _delete():
        time.sleep(delay)
        try:
            bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
    threading.Thread(target=_delete, daemon=True).start()

def send_report(bot, chat_id, text, delete_after=5):
    """Отправляет отчёт и удаляет его через delete_after секунд"""
    msg = bot.send_message(chat_id, text)
    if delete_after > 0:
        safe_delete(msg, delete_after)

def download_file(bot, file_id, suffix=""):
    """Скачивает файл из Telegram во временную папку"""
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)
    temp_path = f"/tmp/telegram_file_{file_id}_{suffix}"
    with open(temp_path, "wb") as f:
        f.write(downloaded)
    return temp_path

# ==========================================
# АВТОРИЗАЦИЯ
# ==========================================
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

# ==========================================
# КЛАВИАТУРЫ
# ==========================================
def get_admin_menu():
    return get_admin_menu_keyboard()

def get_user_menu():
    return get_user_menu_keyboard()

def get_moods_keyboard():
    """Клавиатура для выбора настроения"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    try:
        from dialogue.user_settings import MOODS
        for mood_id, mood_data in MOODS.items():
            keyboard.add(InlineKeyboardButton(
                f"{mood_data['emoji']} {mood_data['name']}",
                callback_data=f"set_mood_{mood_id}"
            ))
    except ImportError:
        keyboard.add(InlineKeyboardButton("🎨 Художник", callback_data="set_mood_artist"))
        keyboard.add(InlineKeyboardButton("📋 Администратор", callback_data="set_mood_admin"))
    keyboard.add(InlineKeyboardButton("❌ Закрыть", callback_data="close_mood_menu"))
    return keyboard

def get_dialog_keyboard():
    """Кнопка для начала диалога"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("🗣 Начать диалог", callback_data="start_dialog"))
    return keyboard

# ==========================================
# ОБРАБОТЧИК КОМАНДЫ #админ
# ==========================================
def handle_admin_command(message, bot):
    user_id = message.from_user.id
    text = message.text.lower()
    
    if is_admin_authorized(user_id):
        bot.reply_to(message, "🛡️ Админ-меню:", reply_markup=get_admin_menu())
        safe_delete(message, 3)
        return
    
    parts = text.split(maxsplit=1)
    if len(parts) > 1:
        password = parts[1]
        if authorize_admin(user_id, password):
            bot.reply_to(message, "✅ Авторизация успешна!", reply_markup=get_admin_menu())
            safe_delete(message, 3)
        else:
            msg = bot.reply_to(message, "❌ Неверный пароль.")
            safe_delete(message, 3)
            safe_delete(msg, 5)
        return
    
    bot.reply_to(message, "🔐 Введите пароль для входа в админ-панель:\n(или #админ пароль)")

# ==========================================
# ОБРАБОТЧИКИ КНОПОК
# ==========================================
def show_admin_panel(call, bot):
    bot.edit_message_text(
        "🛡️ *Админ-панель*\n\nВыберите действие:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=get_admin_menu(),
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

def show_add_post_ui(call, bot):
    msg = bot.send_message(
        call.message.chat.id,
        "📝 *Добавление поста*\n\n"
        "Пришлите текст поста (можно с Markdown).\n"
        "Или /cancel для отмены.",
        parse_mode='Markdown'
    )
    safe_delete(call.message, 1)
    bot.register_next_step_handler(msg, process_post_text, bot)

def process_post_text(message, bot):
    if message.text == "/cancel":
        msg = bot.reply_to(message, "❌ Добавление поста отменено.", reply_markup=get_admin_menu())
        safe_delete(message, 3)
        safe_delete(msg, 5)
        return
    
    if not hasattr(process_post_text, "temp_posts"):
        process_post_text.temp_posts = {}
    process_post_text.temp_posts[message.from_user.id] = {"text": message.text}
    
    msg = bot.send_message(
        message.chat.id,
        "🏷️ Введите теги через пробел (например: #тлеем #ансамбль)\n"
        "Или /skip для пропуска"
    )
    bot.register_next_step_handler(msg, process_post_tags, bot, message.from_user.id)
    safe_delete(message, 2)

def process_post_tags(message, bot, user_id):
    if message.text == "/skip":
        tags = []
    elif message.text == "/cancel":
        msg = bot.reply_to(message, "❌ Добавление поста отменено.", reply_markup=get_admin_menu())
        safe_delete(message, 3)
        safe_delete(msg, 5)
        return
    else:
        tags = message.text.split()
    
    post_data = getattr(process_post_text, "temp_posts", {}).get(user_id, {})
    text = post_data.get("text", "")
    
    from dialogue.post_manager import add_post_to_pool
    success = add_post_to_pool(text, tags, author_id=user_id)
    
    if success:
        msg = bot.reply_to(message, "✅ Пост добавлен в пул публикаций!", reply_markup=get_admin_menu())
    else:
        msg = bot.reply_to(message, "❌ Ошибка при сохранении поста.", reply_markup=get_admin_menu())
    
    safe_delete(message, 3)
    safe_delete(msg, 5)

def show_vk_post_ui(call, bot):
    msg = bot.send_message(
        call.message.chat.id,
        "🎬 *Пост в VK*\n\n"
        "Пришлите текст поста (можно с Markdown).\n"
        "Можно добавить несколько фото, видео или документов.\n"
        "Или /cancel для отмены.",
        parse_mode='Markdown'
    )
    safe_delete(call.message, 1)
    bot.register_next_step_handler(msg, process_vk_post, bot)

def process_vk_post(message, bot):
    if message.text == "/cancel":
        msg = bot.reply_to(message, "❌ Отправка в VK отменена.", reply_markup=get_admin_menu())
        safe_delete(message, 3)
        safe_delete(msg, 5)
        return
    
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    if not vk_token or not vk_owner_id:
        report = "❌ VK_TOKEN или VK_OWNER_ID не заданы"
        msg = bot.reply_to(message, report)
        safe_delete(message, 3)
        safe_delete(msg, 10)
        return
    
    file_paths = []
    
    if hasattr(message, 'photo') and message.photo:
        for photo in message.photo:
            temp_path = download_file(bot, photo.file_id, f"vk_photo_{photo.file_id}.jpg")
            file_paths.append(temp_path)
    
    if hasattr(message, 'video') and message.video:
        temp_path = download_file(bot, message.video.file_id, f"vk_video_{message.video.file_id}.mp4")
        file_paths.append(temp_path)
    
    if hasattr(message, 'document') and message.document:
        temp_path = download_file(bot, message.document.file_id, f"vk_doc_{message.document.file_id}")
        file_paths.append(temp_path)
    
    caption = message.caption or ""
    
    from dialogue.publisher_utils import post_to_vk
    success, result = post_to_vk(caption, "", vk_token, vk_owner_id, file_paths if file_paths else None)
    
    if success:
        report = f"✅ Пост опубликован в VK!\n{result}"
    else:
        report = f"❌ Ошибка VK: {result}"
    
    msg = bot.reply_to(message, report)
    safe_delete(message, 3)
    safe_delete(msg, 10)
    
    for fp in file_paths:
        if os.path.exists(fp):
            try:
                os.remove(fp)
            except:
                pass

def show_quotes_panel(call, bot):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text("list_quotes"), callback_data=get_callback("list_quotes")),
        InlineKeyboardButton(get_text("add_quote"), callback_data=get_callback("add_quote")),
    )
    keyboard.add(
        InlineKeyboardButton(get_text("set_quote_interval"), callback_data=get_callback("set_quote_interval")),
        InlineKeyboardButton(get_text("back_to_admin"), callback_data=get_callback("back_to_admin")),
    )
    bot.edit_message_text(
        "📜 *Управление цитатами*\n\n"
        f"📊 Всего цитат: {len(get_quotes_list())}\n"
        f"⏱️ Интервал публикации: {get_quotes_interval()} мин.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

def list_quotes(call, bot):
    quotes = get_quotes_list()
    if not quotes:
        bot.edit_message_text(
            "📭 База цитат пуста.\n\nДобавьте цитаты через #админ.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(get_text("back_to_admin"), callback_data=get_callback("back_to_admin"))
            )
        )
        return
    
    text = "📖 *Последние 20 цитат:*\n\n"
    for i, q in enumerate(quotes[-20:], 1):
        text += f"{i}. {q[:80]}{'...' if len(q) > 80 else ''}\n"
    
    bot.edit_message_text(
        text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(get_text("back_to_admin"), callback_data=get_callback("back_to_admin"))
        ),
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

def add_quote_ui(call, bot):
    msg = bot.send_message(
        call.message.chat.id,
        "📜 *Добавление цитаты*\n\n"
        "Пришлите текст цитаты (можно на нескольких строках).\n"
        "Или /cancel для отмены.",
        parse_mode='Markdown'
    )
    safe_delete(call.message, 1)
    bot.register_next_step_handler(msg, process_new_quote, bot)

def process_new_quote(message, bot):
    if message.text == "/cancel":
        msg = bot.reply_to(message, "❌ Добавление цитаты отменено.", reply_markup=get_admin_menu())
        safe_delete(message, 3)
        safe_delete(msg, 5)
        return
    
    quote = message.text.strip()
    if add_quote(quote):
        msg = bot.reply_to(message, "✅ Цитата добавлена в базу!", reply_markup=get_admin_menu())
    else:
        msg = bot.reply_to(message, "❌ Ошибка при сохранении цитаты.", reply_markup=get_admin_menu())
    
    safe_delete(message, 3)
    safe_delete(msg, 5)

def set_quote_interval_ui(call, bot):
    msg = bot.send_message(
        call.message.chat.id,
        f"⏱️ *Текущий интервал цитат:* {get_quotes_interval()} мин.\n\n"
        "Введите новое значение в минутах (число от 5 до 720).\n"
        "Или /cancel для отмены.",
        parse_mode='Markdown'
    )
    safe_delete(call.message, 1)
    bot.register_next_step_handler(msg, process_quote_interval, bot)

def process_quote_interval(message, bot):
    if message.text == "/cancel":
        msg = bot.reply_to(message, "❌ Изменение интервала отменено.", reply_markup=get_admin_menu())
        safe_delete(message, 3)
        safe_delete(msg, 5)
        return
    
    try:
        interval = int(message.text.strip())
        if interval < 5 or interval > 720:
            raise ValueError
        set_quotes_interval(interval)
        msg = bot.reply_to(message, f"✅ Интервал цитат установлен на {interval} минут.", reply_markup=get_admin_menu())
    except ValueError:
        msg = bot.reply_to(message, "❌ Ошибка: введите число от 5 до 720.", reply_markup=get_admin_menu())
    
    safe_delete(message, 3)
    safe_delete(msg, 5)

def show_diagnostics(call, bot):
    from dialogue.admin.diagnostics import get_diagnostics_menu
    bot.edit_message_text(
        "📋 *Диагностика*\n\n"
        "Выберите действие:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=get_diagnostics_menu(),
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

def admin_logout(call, bot):
    """Завершает сессию админа с полным удалением сообщения"""
    user_id = call.from_user.id
    logout_admin(user_id)
    # Удаляем сообщение с кнопками
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    # Отправляем короткое подтверждение и тоже удаляем через 3 секунды
    msg = bot.send_message(
        call.message.chat.id,
        "👋 Вы вышли из админ-панели.\n\nДля входа используйте #админ"
    )
    safe_delete(msg, 3)
    bot.answer_callback_query(call.id)

# ==========================================
# ПОДМЕНЮ «НАСТРОЕНИЕ» И ДИАЛОГ
# ==========================================
def show_mood_menu(call, bot):
    """Показывает меню выбора настроения"""
    bot.edit_message_text(
        "🎭 *Выберите настроение*\n\n"
        "От этого зависит стиль ответов агента.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=get_moods_keyboard(),
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

def show_dialog_ui(call, bot):
    """Кнопка начала диалога (вместо #говори)"""
    msg = bot.send_message(
        call.message.chat.id,
        "🗣 *Начните диалог*\n\n"
        "Просто напишите сообщение — я передам его агенту.",
        parse_mode='Markdown'
    )
    safe_delete(call.message, 1)
    bot.register_next_step_handler(msg, process_dialog_message, bot)

def process_dialog_message(message, bot):
    """Обрабатывает сообщение от пользователя (диалог с агентом)"""
    from dialogue.agent import ask_agent
    
    # Показываем, что агент думает
    status_msg = bot.reply_to(message, "⏳ Старший брат думает...")
    
    answer = ask_agent(message.text)
    
    # Удаляем статус
    try:
        bot.delete_message(status_msg.chat.id, status_msg.message_id)
    except:
        pass
    
    if answer:
        bot.reply_to(message, f"🗣 *Старший брат:*\n{answer}", parse_mode='Markdown')
    else:
        bot.reply_to(message, "🌙 Старший брат отдыхает. Попробуй позже.")
    
    # Удаляем сообщение пользователя через 5 секунд (опционально)
    safe_delete(message, 5)

# ==========================================
# ВРЕМЕННОЕ ХРАНИЛИЩЕ
# ==========================================
if not hasattr(process_post_text, "temp_posts"):
    process_post_text.temp_posts = {}
