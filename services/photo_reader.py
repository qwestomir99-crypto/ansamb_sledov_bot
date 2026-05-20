# ==========================================
# Модуль: services/photo_reader.py
# Задача: получать случайный пост (текст + фото) из группы VK
# ==========================================

import random
import requests
import os
import json

# Файл для кэша постов
CACHE_FILE = "dialogue/data/vk_posts_cache.json"

# ID группы «Сапёры Аутентичности» (отрицательное число!)
VK_GROUP_ID = -226615780

# Токен VK из переменных окружения
VK_TOKEN = os.environ.get("VK_TOKEN")

def load_posts_cache():
    """Загружает кэш постов из файла"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_posts_cache(posts):
    """Сохраняет кэш постов в файл"""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def fetch_posts_from_vk():
    """Получает все посты со стены группы VK, включая текст и фото"""
    if not VK_TOKEN:
        print("[PHOTO] ❌ Нет VK_TOKEN")
        return []
    
    posts = []
    offset = 0
    count = 100  # максимум за раз
    
    print("[PHOTO] Загрузка постов из VK...")
    
    while True:
        url = "https://api.vk.com/method/wall.get"
        params = {
            "owner_id": VK_GROUP_ID,
            "count": count,
            "offset": offset,
            "access_token": VK_TOKEN,
            "v": "5.199"
        }
        
        try:
            r = requests.get(url, params=params, timeout=15)
            data = r.json()
            
            if "error" in data:
                print(f"[PHOTO] ❌ Ошибка VK: {data['error']['error_msg']}")
                break
            
            items = data.get("response", {}).get("items", [])
            if not items:
                break
            
            for post in items:
                # Пропускаем закреплённые посты
                if post.get("is_pinned"):
                    continue
                
                text = post.get("text", "").strip()
                if not text:
                    continue
                
                # Ищем первую фотографию в посте
                photo_url = None
                attachments = post.get("attachments", [])
                for att in attachments:
                    if att["type"] == "photo":
                        sizes = att["photo"]["sizes"]
                        if sizes:
                            photo_url = sizes[-1]["url"]  # самое большое
                            break
                
                # Пост без фото — пропускаем
                if not photo_url:
                    continue
                
                # Извлекаем хештеги из текста
                tags = [word for word in text.split() if word.startswith('#')]
                
                posts.append({
                    "text": text,
                    "photo_url": photo_url,
                    "tags": tags,
                    "post_id": post.get("id"),
                    "date": post.get("date")
                })
            
            offset += count
            if len(items) < count:
                break
                
        except Exception as e:
            print(f"[PHOTO] ❌ Ошибка: {e}")
            break
    
    print(f"[PHOTO] ✅ Загружено {len(posts)} постов с фото")
    return posts

def get_random_post(force_refresh=False):
    """Возвращает случайный пост из кэша или из VK"""
    posts = []
    
    if not force_refresh:
        posts = load_posts_cache()
    
    if not posts:
        posts = fetch_posts_from_vk()
        if posts:
            save_posts_cache(posts)
    
    if not posts:
        return None
    
    return random.choice(posts)

def get_random_photo(force_refresh=False):
    """Для обратной совместимости — возвращает только URL случайного фото"""
    post = get_random_post(force_refresh)
    if post:
        return post.get("photo_url")
    return None
