# ==========================================
# Файл: dialogue/publisher_utils.py
# Справка: README.md → Публикатор / Утилиты
# Задача: отправка постов в Telegram и VK с поддержкой медиа
# Комментарий: использует utils.escape_markdown для безопасной отправки текста
# Зависит от: requests, os, random, json, utils
# Вызывается из: publisher.py
# ==========================================

import requests
import os
import random
import json
import time
from datetime import datetime
from utils import escape_markdown

CONFIG_FILE = "config.json"
QUOTES_FILE = "dialogue/data/quotes.txt"
VK_POSTS_FILE = "dialogue/data/vk_posts.json"

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

def load_vk_posts():
    if not os.path.exists(VK_POSTS_FILE):
        return []
    with open(VK_POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_random_own_post_from_vk():
    posts = load_vk_posts()
    if not posts:
        return None
    
    posts_with_media = [p for p in posts if p.get("attachments") or p.get("text")]
    if not posts_with_media:
        posts_with_media = posts
    
    post = random.choice(posts_with_media)
    return {
        "post_id": post.get("id"),
        "text": post.get("text", ""),
        "attachments": post.get("attachments", []),
        "date": post.get("date")
    }

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
        print(f"[VK] upload URL ошибка: {e}")
        return None

def upload_photo_to_vk(upload_url, file_path, vk_token):
    try:
        with open(file_path, 'rb') as f:
            files = {'photo': f}
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
            print(f"[VK] save photo ошибка: {photo_data}")
            return None
    except Exception as e:
        print(f"[VK] upload photo ошибка: {e}")
        return None

def post_to_vk(message, tags, access_token, owner_id, file_path=None, auto_quote=True, auto_tags=True, repost_from=None):
    """Отправляет пост в VK с экранированием для MarkdownV2."""
    print(f"[VK] post_to_vk вызван: message={message[:50]}..., repost_from={repost_from}")
    
    if not access_token or not owner_id:
        print("[VK] Нет токена или owner_id")
        return False, "❌ Ошибка авторизации VK. Проверь токен."
    
    if auto_quote and message and len(message) < 500:
        quote = get_random_quote()
        message = f"{message}\n\n📜 {quote}"
        print(f"[VK] Добавлена цитата: {quote[:50]}...")
    
    if auto_tags:
        tags = get_auto_tags(message, "vk")
        print(f"[VK] Теги: {tags}")
    
    full_message = f"{message}\n\n{tags}" if message else tags
    
    params = {
        "access_token": access_token,
        "v": "5.199",
        "owner_id": owner_id,
        "message": full_message,
        "from_group": 1
    }
    
    # Репост
    if repost_from and repost_from.get("attachments"):
        attachments = []
        for att in repost_from["attachments"][:5]:
            if att.get("type") == "photo":
                photo = att.get("photo", {})
                if photo.get("owner_id") and photo.get("id"):
                    attachments.append(f"photo{photo['owner_id']}_{photo['id']}")
            elif att.get("type") == "video":
                video = att.get("video", {})
                if video.get("owner_id") and video.get("id"):
                    attachments.append(f"video{video['owner_id']}_{video['id']}")
        if attachments:
            params['attachments'] = ",".join(attachments)
            print(f"[VK] Прикреплены вложения из репоста: {len(attachments)}")
    
    # Прямой файл
    elif file_path and os.path.exists(file_path):
        print(f"[VK] Файл найден: {file_path}")
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            upload_url = get_vk_upload_url(access_token, owner_id)
            if upload_url:
                photo_attachment = upload_photo_to_vk(upload_url, file_path, access_token)
                if photo_attachment:
                    params['attachments'] = photo_attachment
                    print(f"[VK] Фото прикреплено: {photo_attachment}")
                else:
                    print("[VK] Не удалось загрузить фото")
            else:
                print("[VK] Не удалось получить upload URL")
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            print("[VK] Видео пока не поддерживается")
        else:
            print(f"[VK] Неподдерживаемый тип файла {ext}")
    
    try:
        r = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=30)
        data = r.json()
        if 'response' in data:
            print(f"[VK] ✅ опубликовано: {message[:50]}...")
            return True, None
        else:
            print(f"[VK] ошибка: {data}")
            return False, f"❌ Ошибка VK: {data.get('error', {}).get('error_msg', 'неизвестная')}"
    except Exception as e:
        print(f"[VK] исключение: {e}")
        return False, f"❌ Ошибка сети: {e}"

def post_to_telegram(bot, chat_id, message, file_path=None, tags=None, auto_quote=True, auto_tags=True):
    """Отправляет пост в Telegram с экранированием caption."""
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
    
    # Экранируем caption для Telegram
    safe_caption = escape_markdown(full_message) if full_message else None
    
    try:
        if file_path and os.path.exists(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                with open(file_path, 'rb') as f:
                    if safe_caption:
                        bot.send_photo(chat_id, f, caption=safe_caption, parse_mode='MarkdownV2')
                    else:
                        bot.send_photo(chat_id, f)
            elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
                with open(file_path, 'rb') as f:
                    if safe_caption:
                        bot.send_video(chat_id, f, caption=safe_caption, parse_mode='MarkdownV2')
                    else:
                        bot.send_video(chat_id, f)
            elif ext in ['.mp3', '.m4a', '.wav']:
                with open(file_path, 'rb') as f:
                    if safe_caption:
                        bot.send_audio(chat_id, f, caption=safe_caption, parse_mode='MarkdownV2')
                    else:
                        bot.send_audio(chat_id, f)
            else:
                with open(file_path, 'rb') as f:
                    if safe_caption:
                        bot.send_document(chat_id, f, caption=safe_caption, parse_mode='MarkdownV2')
                    else:
                        bot.send_document(chat_id, f)
        else:
            if safe_caption:
                bot.send_message(chat_id, safe_caption, parse_mode='MarkdownV2')
            else:
                print(f"[PUBLISHER] Нет текста и файла для публикации в {chat_id}")
                return False
        return True
    except Exception as e:
        print(f"[PUBLISHER] Ошибка Telegram: {e}")
        return False
