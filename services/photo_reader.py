# ==========================================
# Файл: services/photo_reader.py
# Справка: README.md → Фото-ридер
# Задача: получать случайный пост (текст + фото) с твоей стены VK
# Комментарий: чистая версия, без лишнего. Берёт только посты с фото.
# Зависит от: requests, os, json, random
# Вызывается из: dialogue/quotes.py
# ==========================================

import os
import json
import random
import requests

CACHE_FILE = "dialogue/data/vk_posts_cache.json"

def get_vk_token():
    return os.environ.get("VK_TOKEN")

def get_vk_owner_id():
    return os.environ.get("VK_OWNER_ID")

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_cache(posts):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def fetch_wall_posts():
    """Загружает посты с твоей стены VK"""
    token = get_vk_token()
    owner_id = get_vk_owner_id()
    
    if not token or not owner_id:
        print("[PHOTO] ❌ Нет VK_TOKEN или VK_OWNER_ID")
        return []
    
    url = "https://api.vk.com/method/wall.get"
    params = {
        "owner_id": owner_id,
        "count": 100,
        "access_token": token,
        "v": "5.199"
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        
        if "error" in data:
            print(f"[PHOTO] ❌ Ошибка VK API: {data['error']['error_msg']}")
            return []
        
        items = data.get("response", {}).get("items", [])
        print(f"[PHOTO] ✅ Получено {len(items)} постов")
        
        posts = []
        for post in items:
            if post.get("is_pinned"):
                continue
            
            text = post.get("text", "").strip()
            if not text:
                continue
            
            # Ищем первую фотографию
            photo_url = None
            attachments = post.get("attachments", [])
            for att in attachments:
                if att.get("type") == "photo":
                    sizes = att.get("photo", {}).get("sizes", [])
                    if sizes:
                        photo_url = sizes[-1]["url"]
                        break
            
            if not photo_url:
                continue
            
            # Извлекаем хештеги
            tags = [w for w in text.split() if w.startswith('#')]
            
            posts.append({
                "text": text,
                "photo_url": photo_url,
                "tags": tags,
                "post_id": post.get("id")
            })
        
        print(f"[PHOTO] ✅ Найдено {len(posts)} постов с фото")
        return posts
        
    except Exception as e:
        print(f"[PHOTO] ❌ Ошибка запроса: {e}")
        return []

def get_random_post(force_refresh=False):
    """Возвращает случайный пост с фото"""
    posts = []
    
    if not force_refresh:
        posts = load_cache()
    
    if not posts:
        posts = fetch_wall_posts()
        if posts:
            save_cache(posts)
    
    if not posts:
        return None
    
    return random.choice(posts)

# Для теста
if __name__ == "__main__":
    print("=== ТЕСТ PHOTO_READER ===")
    post = get_random_post()
    if post:
        print(f"Текст: {post['text'][:100]}...")
        print(f"Фото: {post['photo_url'][:80]}...")
        print(f"Теги: {post['tags']}")
    else:
        print("❌ Нет постов с фото")
