# ==========================================
# Файл: services/photo_reader.py
# Справка: README.md → Репосты из VK
# Задача: получить случайный пост с доступным фото с твоей стены VK
# Комментарий: использует VK_READER_TOKEN
# ==========================================

import os
import random
import requests
from debug_utils import debug_log

# Загружаем переменные из .env
from dotenv import load_dotenv
load_dotenv()

def get_random_post():
    token = os.environ.get("VK_READER_TOKEN")
    owner_id = os.environ.get("VK_OWNER_ID")
    
    if not token or not owner_id:
        debug_log("PHOTO_READER", "Нет VK_READER_TOKEN или VK_OWNER_ID", "ERROR")
        return None
    
    url = "https://api.vk.com/method/wall.get"
    params = {
        "owner_id": owner_id,
        "count": 50,
        "access_token": token,
        "v": "5.199"
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        
        if "error" in data:
            debug_log("PHOTO_READER", f"Ошибка: {data['error']['error_msg']}", "ERROR")
            return None
        
        items = data.get("response", {}).get("items", [])
        posts_with_photo = []
        for post in items:
            if post.get("is_pinned"):
                continue
            text = post.get("text", "").strip()
            if not text:
                continue
            attachments = post.get("attachments", [])
            for att in attachments:
                if att.get("type") == "photo":
                    sizes = att.get("photo", {}).get("sizes", [])
                    if sizes:
                        photo_url = sizes[-1]["url"]
                        try:
                            head = requests.head(photo_url, timeout=5)
                            if head.status_code == 200:
                                tags = [w for w in text.split() if w.startswith('#')]
                                posts_with_photo.append({
                                    "text": text,
                                    "photo_url": photo_url,
                                    "tags": tags
                                })
                        except:
                            pass
                        break
        
        if not posts_with_photo:
            debug_log("PHOTO_READER", "Нет доступных постов с фото", "WARNING")
            return None
        
        debug_log("PHOTO_READER", f"Найдено {len(posts_with_photo)} постов с доступными фото")
        return random.choice(posts_with_photo)
        
    except Exception as e:
        debug_log("PHOTO_READER", f"Ошибка: {e}", "ERROR")
        return None
