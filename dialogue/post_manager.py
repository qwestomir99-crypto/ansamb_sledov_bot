# ==========================================
# Файл: dialogue/post_manager.py
# Справка: README.md → Пул постов
# Задача: хранение, добавление, удаление, выбор постов с учётом веса
# Комментарий: используется publisher.py для получения следующего поста
# Зависит от: json, os, random, datetime
# Вызывается из: publisher.py, admin_commands.py
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
    """Загружает пул постов из JSON"""
    if not os.path.exists(POST_POOL_FILE):
        return []
    with open(POST_POOL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_post_pool(pool):
    """Сохраняет пул постов в JSON"""
    with open(POST_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(pool, f, indent=2, ensure_ascii=False)

def add_post_to_pool(text, tags=None, author="qwestomir", source="admin", weight=80):
    """Добавляет новый пост в пул"""
    pool = load_post_pool()
    new_post = {
        "text": text,
        "tags": tags or [],
        "author": author,
        "weight": weight,
        "added": datetime.now().strftime("%Y-%m-%d"),
        "last_posted": None,
        "source": source
    }
    pool.append(new_post)
    save_post_pool(pool)
    return True

def remove_post_from_pool(index):
    """Удаляет пост из пула по индексу"""
    pool = load_post_pool()
    if 0 <= index < len(pool):
        pool.pop(index)
        save_post_pool(pool)
        return True
    return False

def update_post_last_posted(index):
    """Обновляет время последней публикации поста"""
    pool = load_post_pool()
    if 0 <= index < len(pool):
        pool[index]["last_posted"] = datetime.now().isoformat()
        save_post_pool(pool)
        return True
    return False

def select_post_by_weight():
    """
    Выбирает пост с учётом веса.
    Чем выше weight, тем больше шансов.
    """
    pool = load_post_pool()
    if not pool:
        return None
    
    # Собираем веса
    weights = [post.get("weight", 50) for post in pool]
    total_weight = sum(weights)
    
    if total_weight == 0:
        return random.choice(pool)
    
    # Случайный выбор с учётом веса
    r = random.uniform(0, total_weight)
    cumulative = 0
    for i, post in enumerate(pool):
        cumulative += post.get("weight", 50)
        if r <= cumulative:
            return post, i
    
    return pool[0], 0

def build_tags(post):
    """
    Собирает финальные теги для поста:
    - default_tags из config
    - vk_tags (если VK включён)
    - дополнительные теги из поста
    - тег автора
    """
    config = load_config()
    tags = set()
    
    # Базовые теги
    default_tags = config.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")
    tags.update(default_tags.split())
    
    # Тег автора
    author = post.get("author", "qwestomir")
    tags.add(f"#{author}")
    
    # Дополнительные теги из поста
    extra_tags = post.get("tags", [])
    tags.update(extra_tags)
    
    # Теги для VK (если нужны)
    vk_enabled = config.get("autoposter", {}).get("vk_enabled", True)
    if vk_enabled:
        vk_tags = config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
        tags.update(vk_tags.split())
    
    return " ".join(tags)

def get_post_for_publishing():
    """
    Возвращает пост для публикации и его индекс.
    Автоматически обновляет last_posted.
    """
    post, index = select_post_by_weight()
    if post:
        update_post_last_posted(index)
    return post, index

def get_posts_list():
    """Возвращает список всех постов (для админки)"""
    return load_post_pool()
