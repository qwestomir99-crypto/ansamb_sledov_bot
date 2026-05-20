# ==========================================
# Модуль: dialogue/vk_reader.py
# Справка: README.md → VK Reader
# Задача: читает посты с твоей стены ВК, сохраняет в кэш (текст + фото)
# Комментарий: ритм 0,8 Гц. При первом запуске грузит 100 постов — чтобы архив не пылился.
# Зависит от: config.json, VK_TOKEN, VK_OWNER_ID
# Вызывается из: bot.py
# ==========================================

import time
import json
import os
import requests
from datetime import datetime
from debug_utils import debug_log

CONFIG_FILE = "config.json"
VK_POSTS_FILE = "dialogue/data/vk_posts.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_vk_posts():
    """Загружает сохранённые посты VK из файла (кэш для фото)"""
    if not os.path.exists(VK_POSTS_FILE):
        return []
    with open(VK_POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_vk_posts(posts):
    """Сохраняет посты VK в файл — кэш живёт здесь"""
    os.makedirs(os.path.dirname(VK_POSTS_FILE), exist_ok=True)
    with open(VK_POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

def add_vk_post(post):
    """Добавляет пост в кэш. Если уже есть — не дублируем (Сапёр не любит повторов)"""
    posts = load_vk_posts()
    for p in posts:
        if p.get("id") == post.get("id"):
            return
    posts.append(post)
    save_vk_posts(posts)
    debug_log("VK_READER", f"📥 Пост сохранён: {post.get('text', '')[:50]}...")

def fetch_last_posts(vk_token, owner_id, count=5):
    """Получает последние посты из VK (с фото)"""
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
                # Извлекаем фото, если есть
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
    """
    Главный цикл VK Reader.
    Ритм: проверка каждую минуту. При первом запуске грузим 100 постов,
    чтобы старые картины не пылились в архиве, а шли в дело.
    """
    if not vk_token or not owner_id:
        debug_log("VK_READER", "❌ Нет токена или owner_id — выходим.", "ERROR")
        return

    debug_log("VK_READER", "🔁 Поток запущен. Сапёр на посту. Последний ID = 0")

    last_post_id = None
    posts = load_vk_posts()
    if posts:
        last_post_id = posts[-1].get("id")
        debug_log("VK_READER", f"📦 Загружено {len(posts)} постов из кэша")

    initial_load_done = len(posts) > 0

    while True:
        try:
            # Первый запуск: тянем 100 постов, чтобы наполнить кэш
            if not initial_load_done:
                debug_log("VK_READER", "🚀 Первый запуск: загружаю 100 постов с твоей стены...")
                new_posts = fetch_last_posts(vk_token, owner_id, count=100)
                initial_load_done = True
            else:
                new_posts = fetch_last_posts(vk_token, owner_id, count=3)

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

        time.sleep(60)  # Ритм 0,8 Гц = проверка раз в минуту
