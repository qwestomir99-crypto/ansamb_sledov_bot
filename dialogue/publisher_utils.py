# ==========================================
# Модуль: dialogue/publisher_utils.py
# Справка: README.md → Публикатор
# Задача: отправка постов в Telegram и VK с поддержкой медиа
# Комментарий: автоматически подбирает цитату и теги, если не переданы
# Зависит от: config.json, quotes.txt, post_pool.json
# Вызывается из: publisher.py, admin_commands.py
# ==========================================

import requests
import os
import random
import json
from datetime import datetime

CONFIG_FILE = "config.json"
QUOTES_FILE = "dialogue/data/quotes.txt"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_quotes():
    """Загружает цитаты для автоматической вставки"""
    if not os.path.exists(QUOTES_FILE):
        return []
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_random_quote():
    """Возвращает случайную цитату"""
    quotes = load_quotes()
    return random.choice(quotes) if quotes else "Ритм 0,8 Гц стабилен. Сеть тлеет."

def get_auto_tags(text, platform="vk"):
    """Автоматически подбирает теги из текста и post_pool.json"""
    config = load_config()
    tags = set()
    
    # Базовые теги платформы
    if platform == "vk":
        vk_tags = config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
        tags.update(vk_tags.split())
    else:
        default_tags = config.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")
        tags.update(default_tags.split())
    
    # Ищем теги в тексте (хештеги)
    words = text.split()
    for w in words:
        if w.startswith('#'):
            tags.add(w)
    
    # Пытаемся найти похожий пост в пуле и взять его теги
    pool_file = "dialogue/data/post_pool.json"
    if os.path.exists(pool_file):
        with open(pool_file, "r", encoding="utf-8") as f:
            pool = json.load(f)
        for post in pool:
            if post.get("text") and post["text"].lower() in text.lower():
                extra_tags = post.get("tags", [])
                tags.update(extra_tags)
                break
    
    return " ".join(tags)

def get_vk_upload_url(vk_token, owner_id):
    """Получает URL для загрузки фото в VK"""
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
    """Загружает фото на сервер VK"""
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

def post_to_vk(message, tags, access_token, owner_id, file_path=None, auto_quote=True, auto_tags=True):
    """Отправляет пост в VK с поддержкой медиа и авто-тегов/цитат"""
    if not access_token or not owner_id:
        print("[VK] Нет токена или owner_id")
        return False
    
    # Автоматически подбираем цитату
    if auto_quote and message and len(message) < 500:
        quote = get_random_quote()
        message = f"{message}\n\n📜 {quote}"
    
    # Автоматически подбираем теги
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
    
    # Загружаем фото, если есть
    if file_path and os.path.exists(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            upload_url = get_vk_upload_url(access_token, owner_id)
            if upload_url:
                photo_attachment = upload_photo_to_vk(upload_url, file_path, access_token)
                if photo_attachment:
                    params['attachments'] = photo_attachment
        else:
            print(f"[VK] неподдерживаемый тип файла {ext}")
    
    try:
        r = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=10)
        data = r.json()
        if 'response' in data:
            print(f"[VK] ✅ опубликовано: {message[:50]}...")
            return True
        else:
            print(f"[VK] ошибка: {data}")
            return False
    except Exception as e:
        print(f"[VK] исключение: {e}")
        return False

def post_to_telegram(bot, chat_id, message, file_path=None, tags=None, auto_quote=True, auto_tags=True):
    """Отправляет пост в Telegram с поддержкой медиа и авто-тегов/цитат"""
    # Автоматически подбираем цитату
    if auto_quote and message and len(message) < 500:
        quote = get_random_quote()
        message = f"{message}\n\n📜 {quote}"
    
    # Автоматически подбираем теги
    if auto_tags:
        tags = get_auto_tags(message, "tg")
    
    full_message = message
    if tags and message:
        full_message = f"{message}\n\n{tags}"
    elif tags and not message:
        full_message = tags
    
    try:
        if file_path and os.path.exists(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                with open(file_path, 'rb') as f:
                    if full_message:
                        bot.send_photo(chat_id, f, caption=full_message, parse_mode='Markdown')
                    else:
                        bot.send_photo(chat_id, f)
            elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
                with open(file_path, 'rb') as f:
                    if full_message:
                        bot.send_video(chat_id, f, caption=full_message, parse_mode='Markdown')
                    else:
                        bot.send_video(chat_id, f)
            else:
                with open(file_path, 'rb') as f:
                    if full_message:
                        bot.send_document(chat_id, f, caption=full_message, parse_mode='Markdown')
                    else:
                        bot.send_document(chat_id, f)
        else:
            if full_message:
                bot.send_message(chat_id, full_message, parse_mode='Markdown')
            else:
                print(f"[PUBLISHER] Нет текста и файла для публикации в {chat_id}")
                return False
        return True
    except Exception as e:
        print(f"[PUBLISHER] Ошибка Telegram: {e}")
        return False
