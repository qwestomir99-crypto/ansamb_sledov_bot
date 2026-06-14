# ==========================================
# Файл: vk_reader.py
# Задача: чтение постов со стены пользователя
# Комментарий: использует VK_READER_TOKEN и VK_OWNER_ID
# ==========================================

import requests
import time
import logging
from datetime import datetime
from debug_utils import debug_log

logger = logging.getLogger(__name__)

# ==========================================
# РАБОТА С БАЗОЙ (если нужно сохранять посты)
# ==========================================
# Здесь можно добавить функции для сохранения постов в SQLite
# Например: save_post_to_db(post)
# ==========================================

def fetch_posts(vk_token: str, owner_id: int, count: int = 5) -> list:
    """Получает последние посты со стены пользователя"""
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
            logger.error(f"Ошибка VK: {data}")
            return []
    except Exception as e:
        logger.error(f"Исключение: {e}")
        return []

def vk_reader_loop(bot, vk_token: str, owner_id: int, chat_id: str):
    """Читает посты со стены и сохраняет в базу"""
    if not vk_token or not owner_id:
        logger.warning("VK токен или owner_id не заданы")
        return
    
    logger.info(f"VK Reader запущен, owner_id={owner_id}")
    last_post_id = None
    
    while True:
        try:
            posts = fetch_posts(vk_token, owner_id, count=3)
            if not posts:
                time.sleep(60)
                continue
            
            for post in reversed(posts):
                if last_post_id is None or post["id"] > last_post_id:
                    # Здесь можно сохранить пост в базу
                    logger.info(f"Новый пост: {post['text'][:50]}...")
                    last_post_id = post["id"]
            
            time.sleep(60)
        except Exception as e:
            logger.error(f"Ошибка в цикле: {e}")
            time.sleep(60)
