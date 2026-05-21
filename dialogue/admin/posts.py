# ==========================================
# Файл: dialogue/admin/posts.py
# Справка: README.md → Админка (публикации)
# Задача: отложенные публикации и постинг в VK
# Комментарий: загрузка видео вынесена в services/vk_uploader.py
# ==========================================

import os
import tempfile
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.publisher import add_publication, load_publications
from dialogue.publisher_utils import get_auto_tags, get_random_quote, post_to_vk
from services.vk_uploader import upload_video_to_vk
from dialogue.admin.auth import log_admin_action
from dialogue.admin.menu import get_admin_menu, get_quotes_submenu

def handle_pub_menu(bot, chat_id, message_id, user_id):
    pubs = load_publications()
    if not pubs:
        bot.edit_message_text("📭 Нет отложенных публикаций", chat_id, message_id)
        return
    
    text = "📋 *Отложенные публикации:*\n\n"
    for i, p in enumerate(pubs):
        status = "✅" if p.get("status") == "published" else "⏳"
        pub_text = p.get("text", "[Без текста]")
        if pub_text and len(pub_text) > 50:
            pub_text = pub_text[:50] + "..."
        text += f"{status} `{pub_text}`\n"
        
        if len(text) > 3500:
            bot.send_message(user_id, text, parse_mode='Markdown')
            text = ""
    
    if text:
        bot.edit_message_text(text, chat_id, message_id, parse_mode='Markdown')
    return_to_admin_menu(bot, chat_id, message_id, user_id)

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
    from dialogue.admin_commands import load_config
    config = load_config()
    pub_config = config.get("publisher", {})
    default_tags = pub_config.get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")
    
    add_publication("telegram", text, delay_seconds, default_tags, file_path)
    user_id = message.from_user.id
    log_admin_action(user_id, f"add_post in {delay_minutes} min, text: {bool(text)}, file: {bool(file_path)}", "success")
    bot.send_message(chat_id, f"✅ Пост запланирован через {delay_minutes} минут")

def handle_vk_post(bot, chat_id, message_id, user_id):
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
        file_path = os.path.join(tempfile.gettempdir(), f"temp_vk_{message.photo[-1].file_id}.jpg")
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
    elif message.video:
        file_info = bot.get_file(message.video.file_id)
        file_path = os.path.join(tempfile.gettempdir(), f"temp_vk_{message.video.file_id}.mp4")
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
    elif message.document:
        ext = os.path.splitext(message.document.file_name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.mkv']:
            file_info = bot.get_file(message.document.file_id)
            file_path = os.path.join(tempfile.gettempdir(), f"temp_vk_{message.document.file_id}_{message.document.file_name}")
            downloaded_file = bot.download_file(file_info.file_path)
            with open(file_path, 'wb') as f:
                f.write(downloaded_file)
    
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    if not vk_token or not vk_owner_id:
        bot.send_message(chat_id, "❌ Нет токена VK. Проверь переменные окружения.")
        return_to_admin_menu(bot, chat_id, user_id=user_id)
        return
    
    quote = get_random_quote()
    full_text = f"{text}\n\n📜 {quote}"
    auto_tags = get_auto_tags(text, "vk")
    
    # Единый сервис загрузки видео (выбор способа по размеру)
    if file_path:
        success, result = upload_video_to_vk(file_path, vk_token, vk_owner_id, full_text, auto_tags)
        if success:
            bot.send_message(chat_id, f"✅ Видео отправлено в VK:\n\n{full_text[:200]}")
        else:
            bot.send_message(chat_id, f"❌ Ошибка: {result}")
    else:
        # Для фото и текста используем старую логику post_to_vk
        success, error_msg = post_to_vk(full_text, auto_tags, vk_token, vk_owner_id, file_path, auto_quote=False, auto_tags=False)
        if success:
            bot.send_message(chat_id, f"✅ Пост отправлен в VK:\n\n{full_text[:200]}")
        else:
            bot.send_message(chat_id, error_msg or "❌ Ошибка при отправке в VK")
    
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
    
    return_to_admin_menu(bot, chat_id, user_id=user_id)

def return_to_admin_menu(bot, chat_id, message_id=None, user_id=None):
    from dialogue.admin_commands import return_to_admin_menu as _return
    _return(bot, chat_id, message_id, user_id)
