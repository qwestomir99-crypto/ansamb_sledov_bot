# ==========================================
# Файл: dialogue/admin_commands.py
# Справка: README.md → Админ-панель
# Задача: админ-меню, кнопки, управление цитатами, постинг в VK
# Комментарий: использует button_map.py для единого управления кнопками
# Зависит от: telebot, button_map, publisher, quotes, diagnostics
# Вызывается из: bot.py (handle_message), callbacks.py
# ==========================================

import os
import random
import json
import threading
import time
from datetime import datetime
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
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
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

# ==========================================
# АВТОРИЗАЦИЯ
# ==========================================
authorized_admins = {}

def is_admin_authorized(user_id):
    """Проверяет, авторизован ли пользователь в админ-панели (по user_id)."""
    return authorized_admins.get(user_id, False)

def authorize_admin(user_id, password):
    """Авторизует админа, если пароль верен."""
    if password == ADMIN_PASSWORD:
        authorized_admins[user_id] = True
        debug_log("ADMIN", f"Админ {user_id} авторизован")
        return True
    return False

def logout_admin(user_id):
    """Завершает сессию админа."""
    if user_id in authorized_admins:
        del authorized_admins[user_id]
        debug_log("ADMIN", f"Админ {user_id} вышел")

# ==========================================
# КЛАВИАТУРЫ (через button_map)
# ==========================================
def get_admin_menu():
    """Возвращает клавиатуру админ-меню (из button_map)."""
    return get_admin_menu_keyboard()

def get_user_menu():
    """Возвращает клавиатуру пользовательского меню (из button_map)."""
    return get_user_menu_keyboard()

# ==========================================
# ОБРАБОТЧИК КОМАНДЫ #админ
# ==========================================
def handle_admin_command(message, bot):
    """
    Обрабатывает команду #админ.
    Запрашивает пароль или открывает меню, если уже авторизован.
    """
    user_id = message.from_user.id
    text = message.text.lower()
    
    # Если уже авторизован — показываем меню
    if is_admin_authorized(user_id):
        bot.reply_to(message, "🛡️ Админ-меню:", reply_markup=get_admin_menu())
        safe_delete(message, 3)
        return
    
    # Если команда содержит пароль (формат: "#админ пароль")
    parts = text.split(maxsplit=1)
    if len(parts) > 1:
        password = parts[1]
        if authorize_admin(user_id, password):
            bot.reply_to(message, "✅ Авторизация успешна! Добро пожаловать в админ-панель.",
                        reply_markup=get_admin_menu())
            safe_delete(message, 3)
        else:
            msg = bot.reply_to(message, "❌ Неверный пароль. Доступ запрещён.")
            safe_delete(message, 3)
            safe_delete(msg, 5)
        return
    
    # Если пароль не передан — запрашиваем
    bot.reply_to(message, "🔐 Введите пароль для входа в админ-панель:\n(или #админ пароль)")

# ==========================================
# ОБРАБОТЧИКИ КНОПОК (вызываются из callbacks.py)
# ==========================================
def show_admin_panel(call, bot):
    """Показывает главную админ-панель."""
    bot.edit_message_text(
        "🛡️ *Админ-панель*\n\nВыберите действие:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=get_admin_menu(),
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

def show_add_post_ui(call, bot):
    """Показывает интерфейс для добавления поста."""
    msg = bot.send_message(
        call.message.chat.id,
        "📝 *Добавление поста*\n\n"
        "Пришлите текст поста (можно с Markdown).\n"
        "Или /cancel для отмены.",
        parse_mode='Markdown'
    )
    # Удаляем сообщение с кнопкой
    safe_delete(call.message, 1)
    # Регистрируем следующий шаг
    bot.register_next_step_handler(msg, process_post_text, bot)

def process_post_text(message, bot):
    """Обрабатывает текст поста и запрашивает теги."""
    if message.text == "/cancel":
        msg = bot.reply_to(message, "❌ Добавление поста отменено.", reply_markup=get_admin_menu())
        safe_delete(message, 3)
        safe_delete(msg, 5)
        return
    
    # Сохраняем текст поста в временное хранилище
    user_id = message.from_user.id
    if not hasattr(process_post_text, "temp_posts"):
        process_post_text.temp_posts = {}
    process_post_text.temp_posts[user_id] = {"text": message.text}
    
    msg = bot.send_message(
        message.chat.id,
        "🏷️ Введите теги через пробел (например: #тлеем #ансамбль)\n"
        "Или /skip для пропуска"
    )
    bot.register_next_step_handler(msg, process_post_tags, bot, user_id)
    safe_delete(message, 2)

def process_post_tags(message, bot, user_id):
    """Обрабатывает теги и создаёт пост."""
    if message.text == "/skip":
        tags = []
    elif message.text == "/cancel":
        msg = bot.reply_to(message, "❌ Добавление поста отменено.", reply_markup=get_admin_menu())
        safe_delete(message, 3)
        safe_delete(msg, 5)
        return
    else:
        tags = message.text.split()
    
    post_data = process_post_text.temp_posts.get(user_id, {})
    text = post_data.get("text", "")
    
    # Сохраняем в post_pool.json
    from dialogue.post_manager import add_post_to_pool
    success = add_post_to_pool(text, tags, author_id=user_id)
    
    if success:
        msg = bot.reply_to(message, "✅ Пост добавлен в пул публикаций!", reply_markup=get_admin_menu())
    else:
        msg = bot.reply_to(message, "❌ Ошибка при сохранении поста.", reply_markup=get_admin_menu())
    
    safe_delete(message, 3)
    safe_delete(msg, 5)

def show_vk_post_ui(call, bot):
    """Показывает интерфейс для отправки поста в VK."""
    msg = bot.send_message(
        call.message.chat.id,
        "🎬 *Пост в VK*\n\n"
        "Пришлите текст поста (можно с Markdown).\n"
        "Можно также добавить фото или видео (одним файлом).\n"
        "Или /cancel для отмены.",
        parse_mode='Markdown'
    )
    safe_delete(call.message, 1)
    bot.register_next_step_handler(msg, process_vk_post, bot)

def process_vk_post(message, bot):
    """Обрабатывает текст/файл и отправляет в VK с отчётом."""
    if message.text == "/cancel":
        msg = bot.reply_to(message, "❌ Отправка в VK отменена.", reply_markup=get_admin_menu())
        safe_delete(message, 3)
        safe_delete(msg, 5)
        return
    
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    if not vk_token or not vk_owner_id:
        report = "❌ VK_TOKEN или VK_OWNER_ID не заданы в переменных окружения"
        msg = bot.reply_to(message, report)
        safe_delete(message, 3)
        safe_delete(msg, 10)
        return
    
    # Если есть файл
    if message.photo or message.video or message.document:
        msg = bot.reply_to(message, "⏳ Отправляю в VK...")
        safe_delete(message, 2)
        
        # Определяем тип файла
        if message.photo:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded = bot.download_file(file_info.file_path)
            temp_path = f"/tmp/vk_photo_{file_id}.jpg"
            with open(temp_path, "wb") as f:
                f.write(downloaded)
        elif message.video:
            file_id = message.video.file_id
            file_info = bot.get_file(file_id)
            downloaded = bot.download_file(file_info.file_path)
            temp_path = f"/tmp/vk_video_{file_id}.mp4"
            with open(temp_path, "wb") as f:
                f.write(downloaded)
        else:
            temp_path = None
        
        # Отправляем в VK
        from services.vk_uploader import post_to_vk_with_media
        success, url = post_to_vk_with_media(message.caption or "", vk_token, vk_owner_id, temp_path)
        
        if success:
            report = f"✅ Пост опубликован в VK!\n{url}"
        else:
            report = f"❌ Ошибка VK: {url}"
        
        final_msg = bot.reply_to(message, report)
        safe_delete(final_msg, 10)
        
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
    else:
        # Только текст
        from dialogue.vk_uploader import post_to_vk
        success, url = post_to_vk(message.text, vk_token, vk_owner_id)
        
        if success:
            report = f"✅ Пост опубликован в VK!\n{url}"
        else:
            report = f"❌ Ошибка VK: {url}"
        
        msg = bot.reply_to(message, report)
        safe_delete(message, 3)
        safe_delete(msg, 10)

def show_quotes_panel(call, bot):
    """Показывает панель управления цитатами."""
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
    """Показывает список цитат (последние 20)."""
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
    """Показывает интерфейс для добавления цитаты."""
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
    """Обрабатывает новую цитату и сохраняет её."""
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
    """Показывает интерфейс для изменения интервала цитат."""
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
    """Устанавливает новый интервал цитат."""
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
    """Показывает панель диагностики."""
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
    """Завершает сессию админа."""
    user_id = call.from_user.id
    logout_admin(user_id)
    bot.edit_message_text(
        "👋 Вы вышли из админ-панели.\n\n"
        "Для входа используйте #админ",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    bot.answer_callback_query(call.id)
