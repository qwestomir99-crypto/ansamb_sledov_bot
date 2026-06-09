# ==========================================
# Модуль: dialogue/vk_reader.py
# Справка: README.md → VK Reader
# Задача: читает посты с твоей стены ВК, сохраняет в кэш (текст + фото)
# Комментарий: использует VK_READER_TOKEN
# ==========================================

import time
import json
import os
import requests
from datetime import datetime
from debug_utils import debug_log

# Путь к файлу конфигурации
CONFIG_FILE = os.path.join('dialogue', 'data', 'config.json')
VK_POSTS_FILE = "dialogue/data/vk_posts.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_vk_posts():
    if not os.path.exists(VK_POSTS_FILE):
        return []
    try:
        with open(VK_POSTS_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except:
        return []

def save_vk_posts(posts):
    os.makedirs(os.path.dirname(VK_POSTS_FILE), exist_ok=True)
    with open(VK_POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

def add_vk_post(post):
    posts = load_vk_posts()
    for p in posts:
        if p.get("id") == post.get("id"):
            return
    posts.append(post)
    save_vk_posts(posts)
    debug_log("VK_READER", f"📥 Пост сохранён: {post.get('text', '')[:50]}...")

def fetch_last_posts(vk_token, owner_id, count=5):
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
        debug_log("VK_READER", f"wall.get ответ: {str(data)[:200]}")
        if "response" in data:
            items = data["response"].get("items", [])
            posts = []
            for item in items:
                photo_url = None
                attachments = item.get("attachments", [])
                for att in attachments:
                    if att.get("type") == "photo":
                        sizes = att.get("photo", {}).get("sizes", [])
                        if sizes:
                            photo_url = sizes[-1]["url"]
                            break
                posts.append({
                    "id": item["id"],
                    "text": item.get("text", ""),
                    "photo_url": photo_url,
                    "date": datetime.fromtimestamp(item["date"]).isoformat(),
                    "likes": item.get("likes", {}).get("count", 0),
                    "reposts": item.get("reposts", {}).get("count", 0),
                    "views": item.get("views", {}).get("count", 0),
                    "comments": item.get("comments", {}).get("count", 0)
                })
            return posts
        else:
            debug_log("VK_READER", f"❌ Ошибка API: {data}", "ERROR")
            return []
    except Exception as e:
        debug_log("VK_READER", f"❌ Ошибка запроса: {e}", "ERROR")
        return []

def vk_reader_loop(bot, vk_token, owner_id, tg_chat_id):
    if not vk_token or not owner_id:
        debug_log("VK_READER", "❌ Нет токена или owner_id — выходим.", "ERROR")
        return

    debug_log("VK_READER", f"🔁 Поток запущен. owner_id={owner_id}, токен длиной={len(vk_token)}")

    last_post_id = None
    posts = load_vk_posts()
    debug_log("VK_READER", f"📦 Загружено из кэша: {len(posts)} постов")
    
    if posts:
        last_post_id = posts[-1].get("id")

    initial_load_done = len(posts) > 0
    debug_log("VK_READER", f"initial_load_done={initial_load_done}")

    debug_log("VK_READER", "Вход в цикл...")
    while True:
        try:
            if not initial_load_done:
                debug_log("VK_READER", "🚀 Первый запуск: загружаю 100 постов с твоей стены...")
                new_posts = fetch_last_posts(vk_token, owner_id, count=100)
                initial_load_done = True
            else:
                new_posts = fetch_last_posts(vk_token, owner_id, count=3)

            debug_log("VK_READER", f"Получено {len(new_posts) if new_posts else 0} новых постов")
            
            if not new_posts:
                time.sleep(60)
                continue

            for post in reversed(new_posts):
                if last_post_id is None or post["id"] > last_post_id:
                    add_vk_post(post)
                    if post["text"]:
                        debug_log("VK_READER", f"🔍 Новый пост: {post['text'][:50]}...")
                    if post.get("photo_url"):
                        debug_log("VK_READER", f"📸 Фото: {post['photo_url'][:60]}...")
                    last_post_id = post["id"]

        except Exception as e:
            debug_log("VK_READER", f"❌ Ошибка цикла: {e}", "ERROR")

        time.sleep(60)
