# ==========================================
# Файл: dialogue/post_manager.py
# Справка: README.md → Пул постов
# Задача: хранение, добавление, удаление, выбор постов с учётом веса
# Комментарий: добавлена поддержка media_url (file_id или ссылка)
# Зависит от: json, os, random, datetime
# Вызывается из: publisher.py, admin_commands.py, message_dispatcher.py
# ==========================================

import json
import os
import random
from datetime import datetime

POST_POOL_FILE = "dialogue/data/post_pool.json"
CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_post_pool():
    if not os.path.exists(POST_POOL_FILE):
        return []
    with open(POST_POOL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_post_pool(pool):
    with open(POST_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(pool, f, indent=2, ensure_ascii=False)

def add_post_to_pool(text, tags=None, author="qwestomir", source="admin", weight=80, media_url=None):
    """Добавляет новый пост в пул (с поддержкой медиа)"""
    pool = load_post_pool()
    new_post = {
        "text": text,
        "tags": tags or [],
        "author": author,
        "weight": weight,
        "added": datetime.now().strftime("%Y-%m-%d"),
        "last_posted": None,
        "source": source,
        "media_url": media_url  # file_id из Telegram или URL
    }
    pool.append(new_post)
    save_post_pool(pool)
    return True

def remove_post_from_pool(index):
    pool = load_post_pool()
    if 0 <= index < len(pool):
        pool.pop(index)
        save_post_pool(pool)
        return True
    return False

def update_post_last_posted(index):
    pool = load_post_pool()
    if 0 <= index < len(pool):
        pool[index]["last_posted"] = datetime.now().isoformat()
        save_post_pool(pool)
        return True
    return False

def select_post_by_weight():
    pool = load_post_pool()
    if not pool:
        return None
    
    weights = [post.get("weight", 50) for post in pool]
    total_weight = sum(weights)
    
    if total_weight == 0:
        return random.choice(pool)
    
    r = random.uniform(0, total_weight)
    cumulative = 0
    for i, post in enumerate(pool):
        cumulative += post.get("weight", 50)
        if r <= cumulative:
            return post, i
    
    return pool[0], 0

def build_tags(post):
    config = load_config()
    tags = set()
    
    default_tags = config.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")
    tags.update(default_tags.split())
    
    author = post.get("author", "qwestomir")
    tags.add(f"#{author}")
    
    extra_tags = post.get("tags", [])
    tags.update(extra_tags)
    
    vk_enabled = config.get("autoposter", {}).get("vk_enabled", True)
    if vk_enabled:
        vk_tags = config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
        tags.update(vk_tags.split())
    
    return " ".join(tags)

def get_post_for_publishing():
    post, index = select_post_by_weight()
    if post:
        update_post_last_posted(index)
    return post, index

def get_posts_list():
    return load_post_pool()
