import time
import json
import os
import requests
from datetime import datetime

CONFIG_FILE = "config.json"
VK_POSTS_FILE = "dialogue/data/vk_posts.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_vk_posts():
    """Загружает сохранённые посты VK из файла"""
    if not os.path.exists(VK_POSTS_FILE):
        return []
    with open(VK_POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_vk_posts(posts):
    """Сохраняет посты VK в файл"""
    os.makedirs(os.path.dirname(VK_POSTS_FILE), exist_ok=True)
    with open(VK_POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

def add_vk_post(post):
    """Добавляет новый пост в историю (если ещё нет)"""
    posts = load_vk_posts()
    # Проверяем, нет ли уже такого поста (по id)
    for p in posts:
        if p.get("id") == post.get("id"):
            return
    posts.append(post)
    save_vk_posts(posts)
    print(f"[VK_READER] Новый пост сохранён: {post.get('text', '')[:50]}...")

def fetch_last_posts(vk_token, owner_id, count=5):
    """Получает последние посты из VK"""
    params = {
        "access_token": vk_token,
        "v": "5.199",
        "owner_id": owner_id,
        "count": count,
        "filter": "owner"
    }
    try:
        r = requests.get("https://api.vk.com/method/wall.get", params=params, timeout=10)
        data = r.json()
        if "response" in data:
            items = data["response"].get("items", [])
            posts = []
            for item in items:
                posts.append({
                    "id": item["id"],
                    "text": item.get("text", ""),
                    "date": datetime.fromtimestamp(item["date"]).isoformat(),
                    "likes": item.get("likes", {}).get("count", 0),
                    "reposts": item.get("reposts", {}).get("count", 0),
                    "views": item.get("views", {}).get("count", 0),
                    "comments": item.get("comments", {}).get("count", 0)
                })
            return posts
        else:
            print(f"[VK_READER] Ошибка API: {data}")
            return []
    except Exception as e:
        print(f"[VK_READER] Ошибка запроса: {e}")
        return []

def vk_reader_loop(bot, vk_token, owner_id, tg_chat_id):
    """Основной цикл чтения VK"""
    if not vk_token or not owner_id:
        print("[VK_READER] Нет токена или owner_id, выход")
        return
    
    print("[VK_READER] Поток запущен, последний ID = 0")
    
    last_post_id = None
    posts = load_vk_posts()
    if posts:
        last_post_id = posts[-1].get("id")
    
    while True:
        try:
            new_posts = fetch_last_posts(vk_token, owner_id, count=3)
            if not new_posts:
                time.sleep(60)
                continue
            
            # Сохраняем новые посты (которых ещё нет в файле)
            for post in reversed(new_posts):
                if last_post_id is None or post["id"] > last_post_id:
                    add_vk_post(post)
                    if post["text"]:
                        print(f"[VK_READER] Новый пост: {post['text'][:50]}...")
                    last_post_id = post["id"]
            
        except Exception as e:
            print(f"[VK_READER] Ошибка цикла: {e}")
        
        time.sleep(60)
