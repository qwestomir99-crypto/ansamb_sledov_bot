# ==========================================
# Файл: services/photo_reader.py
# Задача: получить случайный пост с фото с твоей стены VK
# Комментарий: без кэша, напрямую из VK, каждый раз
# ==========================================

import os
import random
import requests

def get_random_post():
    """Возвращает случайный пост с фото с твоей стены VK"""
    
    token = os.environ.get("VK_TOKEN")
    owner_id = os.environ.get("VK_OWNER_ID")
    
    if not token or not owner_id:
        print("[PHOTO] ❌ Нет VK_TOKEN или VK_OWNER_ID")
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
            print(f"[PHOTO] ❌ Ошибка: {data['error']['error_msg']}")
            return None
        
        items = data.get("response", {}).get("items", [])
        
        # Собираем посты с фото
        posts_with_photo = []
        for post in items:
            if post.get("is_pinned"):
                continue
            
            text = post.get("text", "").strip()
            if not text:
                continue
            
            # Ищем фото
            attachments = post.get("attachments", [])
            for att in attachments:
                if att.get("type") == "photo":
                    sizes = att.get("photo", {}).get("sizes", [])
                    if sizes:
                        photo_url = sizes[-1]["url"]
                        tags = [w for w in text.split() if w.startswith('#')]
                        posts_with_photo.append({
                            "text": text,
                            "photo_url": photo_url,
                            "tags": tags
                        })
                        break
        
        if not posts_with_photo:
            print("[PHOTO] ❌ Нет постов с фото")
            return None
        
        print(f"[PHOTO] ✅ Найдено {len(posts_with_photo)} постов с фото")
        return random.choice(posts_with_photo)
        
    except Exception as e:
        print(f"[PHOTO] ❌ Ошибка: {e}")
        return None
