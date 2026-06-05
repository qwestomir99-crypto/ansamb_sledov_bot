# ==========================================
# Файл: dialogue/publisher.py
# Справка: README.md → Публикатор
# Задача: публикация случайных постов из пула (автоматическая и немедленная)
# Комментарий: для TG — file_id, для VK — media_url (ссылка)
#              Если нет медиа — тематическое фото
#              Старший брат ОТКЛЮЧЁН
#              Лимит пула — 100 постов
#              Выбор поста — случайный (как YouTube из плейлиста)
# Зависит от: os, json, time, random, threading, debug_utils, publisher_utils, post_manager
# Вызывается из: bot.py (поток publish_loop)
# ==========================================

import os
import json
import time
import random
import threading
from debug_utils import debug_log
from dialogue.publisher_utils import post_to_telegram, post_to_vk, get_random_quote
from dialogue.post_manager import load_post_pool, save_post_pool, build_tags, remove_post_from_pool

CONFIG_FILE = "config.json"
MAX_POOL_SIZE = 100

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def clean_pool():
    pool = load_post_pool()
    if len(pool) > MAX_POOL_SIZE:
        pool = pool[-MAX_POOL_SIZE:]
        save_post_pool(pool)
        debug_log("PUBLISH", f"Пул очищен, оставлено {len(pool)} постов")

def get_theme_photo():
    try:
        from services.photo_reader import get_random_post
        post = get_random_post()
        if post and post.get('photo_url'):
            return post['photo_url']
    except:
        pass
    return None

def publish_post_immediately(bot, chat_id, text, tags_str, file_id=None):
    config = load_config()
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    if tg_chat_id:
        return post_to_telegram(bot, tg_chat_id, text, file_id, tags_str)
    return False

def publish_delayed(bot, text, tags_str, delay_seconds, file_id=None):
    time.sleep(delay_seconds)
    config = load_config()
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    publish_post_immediately(bot, tg_chat_id, text, tags_str, file_id)

def publish_from_pool(bot, vk_token, vk_owner_id, tg_chat_id):
    """Публикует СЛУЧАЙНЫЙ пост из пула и удаляет его"""
    pool = load_post_pool()
    if not pool:
        return False
    
    post = random.choice(pool)
    index = pool.index(post)
    
    text = post.get("text", "")
    file_id = post.get("file_id")
    media_url = post.get("media_url")
    tags = build_tags(post)
    quote = get_random_quote()
    
    full_text = f"{text}\n\n📜 {quote}"
    
    success = False
    
    if tg_chat_id:
        try:
            if file_id:
                success = post_to_telegram(bot, tg_chat_id, full_text, file_id, tags)
            elif media_url and media_url.startswith("http"):
                success = post_to_telegram(bot, tg_chat_id, full_text, media_url, tags)
            else:
                theme_photo = get_theme_photo()
                success = post_to_telegram(bot, tg_chat_id, full_text, theme_photo, tags)
            
            if success:
                debug_log("PUBLISH", "Пост опубликован в Telegram")
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка Telegram: {e}", "ERROR")
    
    if success:
        remove_post_from_pool(index)
        debug_log("PUBLISH", f"Пост удалён из пула, осталось {len(load_post_pool())}")
        return True
    
    return False

def publish_loop(bot, vk_token, vk_owner_id, tg_chat_id):
    debug_log("PUBLISH", "Цикл публикации запущен (случайный выбор, лимит: 100)")
    
    while True:
        try:
            try:
                from dialogue.shabbat_manager import is_shabbat
                if is_shabbat():
                    time.sleep(3600)
                    continue
            except ImportError:
                pass
            
            clean_pool()
            
            config = load_config()
            interval = config.get("publisher", {}).get("interval_seconds", 7200)
            
            published = publish_from_pool(bot, vk_token, vk_owner_id, tg_chat_id)
            
            if published:
                debug_log("PUBLISH", f"Опубликовано (случайный пост), следующая через {interval} сек")
            else:
                debug_log("PUBLISH", "Нет постов для публикации")
            
            time.sleep(interval)
            
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка в цикле: {e}", "ERROR")
            time.sleep(300)
