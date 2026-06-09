# ==========================================
# Файл: dialogue/publisher_utils.py
# Справка: README.md → Публикатор / Утилиты
# Задача: отправка постов в Telegram и VK
# Комментарий: VK — сервисный токен сообщества для группы.
#              VK_GROUP_ID уже содержит минус — не дублируем.
# ==========================================

import os
import random
import json
import requests
from utils import escape_markdown
from debug_utils import debug_log

# Путь к файлу конфигурации
CONFIG_FILE = os.path.join('dialogue', 'data', 'config.json')
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

def get_auto_tags(text, platform="vk"):
    config = load_config()
    tags = set()
    if platform == "vk":
        tags.update(config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке").split())
    else:
        tags.update(config.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита").split())
    for w in text.split():
        if w.startswith('#'):
            tags.add(w)
    return " ".join(tags)

def post_to_telegram(bot, chat_id, message, file_id=None, tags=None, auto_quote=True, auto_tags=True):
    if auto_quote and message and len(message) < 500:
        message = f"{message}\n\n📜 {get_random_quote()}"
    if auto_tags:
        tags = get_auto_tags(message, "tg")
    full_message = f"{message}\n\n{tags}" if tags and message else (tags or message)
    try:
        if file_id:
            import telebot
            bot2 = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
            file_info = bot2.get_file(file_id)
            downloaded = bot2.download_file(file_info.file_path)
            ext = os.path.splitext(file_info.file_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                bot.send_photo(chat_id, downloaded, caption=full_message[:1024])
            else:
                bot.send_document(chat_id, downloaded, caption=full_message[:1024])
            return True
        else:
            bot.send_message(chat_id, full_message)
            return True
    except Exception as e:
        debug_log("PUBLISHER", f"Ошибка TG: {e}", "ERROR")
        return False

def post_to_vk(message, tags, access_token, owner_id, file_id=None, auto_quote=True, auto_tags=True, repost_from=None):
    """Публикация в группу VK через сервисный токен сообщества"""
    if not access_token:
        access_token = os.environ.get("VK_TOKEN")
    if not access_token or not owner_id:
        return False, "Ошибка авторизации VK"
    
    if auto_quote and message and len(message) < 500:
        message = f"{message}\n\n📜 {get_random_quote()}"
    if auto_tags:
        tags = get_auto_tags(message, "vk")
    full_message = f"{message}\n\n{tags}" if message else tags
    
    # VK_GROUP_ID уже приходит с минусом — не добавляем лишний
    params = {
        "access_token": access_token,
        "v": "5.199",
        "owner_id": int(owner_id),
        "message": full_message,
        "from_group": 1
    }
    
    try:
        r = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=30)
        data = r.json()
        if 'response' in data:
            debug_log("VK", f"Опубликовано в группе VK, post_id={data['response']['post_id']}")
            return True, None
        else:
            error_msg = data.get('error', {}).get('error_msg', 'неизвестная')
            debug_log("VK", f"Ошибка: {error_msg}", "ERROR")
            return False, f"Ошибка VK: {error_msg}"
    except Exception as e:
        debug_log("VK", f"Исключение: {e}", "ERROR")
        return False, f"Ошибка сети: {e}"
