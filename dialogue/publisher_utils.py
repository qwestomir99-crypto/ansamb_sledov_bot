# ==========================================
# Файл: dialogue/publisher_utils.py
# Справка: README.md → Публикатор / Утилиты
# Задача: отправка постов в Telegram
# Комментарий: VK временно отключён (требуется бизнес-верификация)
# ==========================================

import os
import random
import json
from utils import escape_markdown
from debug_utils import debug_log

CONFIG_FILE = "config.json"
QUOTES_FILE = "dialogue/data/quotes.txt"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_quotes():
    if not os.path.exists(QUOTES_FILE):
        return []
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_random_quote():
    quotes = load_quotes()
    return random.choice(quotes) if quotes else "Ритм 0,8 Гц стабилен. Сеть тлеет."

def get_auto_tags(text, platform="tg"):
    config = load_config()
    tags = set()
    default_tags = config.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")
    tags.update(default_tags.split())
    words = text.split()
    for w in words:
        if w.startswith('#'):
            tags.add(w)
    return " ".join(tags)

def send_media_by_file_id(bot, chat_id, file_id, caption=None):
    try:
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        ext = os.path.splitext(file_info.file_path)[1].lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            bot.send_photo(chat_id, downloaded, caption=caption, parse_mode='MarkdownV2')
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            bot.send_video(chat_id, downloaded, caption=caption, parse_mode='MarkdownV2')
        else:
            bot.send_document(chat_id, downloaded, caption=caption, parse_mode='MarkdownV2')
        return True
    except Exception as e:
        debug_log("PUBLISHER_UTILS", f"Ошибка отправки по file_id: {e}", "WARNING")
        return False

def post_to_telegram(bot, chat_id, message, file_id=None, tags=None, auto_quote=True, auto_tags=True):
    if auto_quote and message and len(message) < 500:
        quote = get_random_quote()
        message = f"{message}\n\n📜 {quote}"
    
    if auto_tags:
        tags = get_auto_tags(message, "tg")
    
    full_message = message
    if tags and message:
        full_message = f"{message}\n\n{tags}"
    elif tags and not message:
        full_message = tags
    
    safe_caption = escape_markdown(full_message) if full_message else None
    
    try:
        if file_id:
            success = send_media_by_file_id(bot, chat_id, file_id, safe_caption)
            if success:
                return True
        
        if safe_caption:
            bot.send_message(chat_id, safe_caption, parse_mode='MarkdownV2')
            return True
        return False
    except Exception as e:
        debug_log("PUBLISHER", f"Ошибка Telegram: {e}", "ERROR")
        try:
            bot.send_message(chat_id, full_message[:4000])
            return True
        except:
            return False

def post_to_vk(message, tags, access_token, owner_id, file_id=None, auto_quote=True, auto_tags=True, repost_from=None):
    """VK временно отключён"""
    debug_log("VK", "VK постинг отключён (требуется бизнес-верификация)", "WARNING")
    return False, "VK временно отключён"
