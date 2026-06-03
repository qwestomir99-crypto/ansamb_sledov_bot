# ==========================================
# Файл: dialogue/publisher_utils.py
# Справка: README.md → Публикатор / Утилиты
# Задача: отправка постов в Telegram и VK
# Комментарий: только критическая диагностика (ошибки и успех)
# ==========================================

import os
import random
import json
import requests
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

def get_auto_tags(text, platform="vk"):
    config = load_config()
    tags = set()
    if platform == "vk":
        vk_tags = config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
        tags.update(vk_tags.split())
    else:
        default_tags = config.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")
        tags.update(default_tags.split())
    words = text.split()
    for w in words:
        if w.startswith('#'):
            tags.add(w)
    return " ".join(tags)

def get_vk_upload_url(vk_token, owner_id):
    params = {
        "access_token": vk_token,
        "v": "5.199",
        "owner_id": owner_id
    }
    try:
        r = requests.get("https://api.vk.com/method/photos.getWallUploadServer", params=params, timeout=10)
        data = r.json()
        return data.get("response", {}).get("upload_url")
    except Exception as e:
        debug_log("VK", f"Ошибка получения URL загрузки: {e}", "ERROR")
        return None

def upload_photo_to_vk(upload_url, file_data, vk_token):
    try:
        files = {'photo': ('photo.jpg', file_data)}
        r = requests.post(upload_url, files=files)
        data = r.json()
        
        save_params = {
            "access_token": vk_token,
            "v": "5.199",
            "photo": data['photo'],
            "server": data['server'],
            "hash": data['hash']
        }
        r = requests.get("https://api.vk.com/method/photos.saveWallPhoto", params=save_params)
        photo_data = r.json()
        
        if 'response' in photo_data and photo_data['response']:
            photo = photo_data['response'][0]
            return f"photo{photo['owner_id']}_{photo['id']}"
        else:
            debug_log("VK", f"Ошибка сохранения фото: {photo_data}", "ERROR")
            return None
    except Exception as e:
        debug_log("VK", f"Ошибка загрузки фото: {e}", "ERROR")
        return None

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
        debug_log("PUBLISHER_UTILS", f"Ошибка отправки по file_id: {e}", "ERROR")
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
        if file_id and isinstance(file_id, str):
            return send_media_by_file_id(bot, chat_id, file_id, safe_caption)
        else:
            if safe_caption:
                bot.send_message(chat_id, safe_caption, parse_mode='MarkdownV2')
            else:
                return False
        return True
    except Exception as e:
        debug_log("PUBLISHER", f"Ошибка Telegram: {e}", "ERROR")
        return False

def post_to_vk(message, tags, access_token, owner_id, file_id=None, auto_quote=True, auto_tags=True, repost_from=None):
    if not access_token or not owner_id:
        debug_log("VK", "Нет токена или owner_id", "ERROR")
        return False, "❌ Ошибка авторизации VK. Проверь токен."
    
    if auto_quote and message and len(message) < 500:
        quote = get_random_quote()
        message = f"{message}\n\n📜 {quote}"
    
    if auto_tags:
        tags = get_auto_tags(message, "vk")
    
    full_message = f"{message}\n\n{tags}" if message else tags
    
    params = {
        "access_token": access_token,
        "v": "5.199",
        "owner_id": owner_id,
        "message": full_message,
        "from_group": 1
    }
    
    attachments = []
    
    # ФОТО ПО file_id
    if file_id:
        try:
            import telebot
            bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
            file_info = bot.get_file(file_id)
            downloaded = bot.download_file(file_info.file_path)
            
            upload_url = get_vk_upload_url(access_token, owner_id)
            if upload_url:
                photo_att = upload_photo_to_vk(upload_url, downloaded, access_token)
                if photo_att:
                    attachments.append(photo_att)
        except Exception as e:
            debug_log("VK", f"Ошибка загрузки фото: {e}", "ERROR")
    
    if attachments:
        params['attachments'] = ",".join(attachments)
    
    try:
        r = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=30)
        data = r.json()
        
        if 'response' in data:
            debug_log("VK", f"Пост опубликован, ID: {data['response']['post_id']}", "INFO")
            return True, None
        else:
            error_msg = data.get('error', {}).get('error_msg', 'неизвестная ошибка')
            debug_log("VK", f"Ошибка: {error_msg}", "ERROR")
            return False, f"❌ Ошибка VK: {error_msg}"
    except Exception as e:
        debug_log("VK", f"Исключение: {e}", "ERROR")
        return False, f"❌ Ошибка сети: {e}"
