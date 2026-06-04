# ==========================================
# Файл: dialogue/publisher.py
# Справка: README.md → Публикатор
# Задача: публикация постов из пула (автоматическая и немедленная)
# Комментарий: публикует посты с цитатами, тегами, фото/видео
#              Если нет медиа — добавляет тематическое фото
#              Старший брат генерирует описание если его нет
#              Лимит пула — 100 постов, старые удаляются
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
    """Оставляет последние MAX_POOL_SIZE постов в пуле"""
    pool = load_post_pool()
    if len(pool) > MAX_POOL_SIZE:
        pool = pool[-MAX_POOL_SIZE:]
        save_post_pool(pool)
        debug_log("PUBLISH", f"Пул очищен, оставлено {len(pool)} постов")

def get_theme_photo():
    """Возвращает случайное тематическое фото если нет медиа"""
    try:
        from services.photo_reader import get_random_post
        post = get_random_post()
        if post and post.get('photo_url'):
            return post['photo_url']
    except:
        pass
    return None

def generate_description(text):
    """Генерирует описание через Старшего брата если текст короткий"""
    try:
        from dialogue.agent import ask_agent
        prompt = f"Опиши это в стиле художественного манифеста, коротко, 2-3 предложения, с ритмом и образами: {text}"
        description = ask_agent(prompt)
        if description and len(description) > 10:
            return description
    except:
        pass
    return None

def publish_post_immediately(bot, chat_id, text, tags_str, file_id=None):
    """Публикует пост немедленно в Telegram и VK"""
    config = load_config()
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID", "607754499")
    
    success_tg = False
    success_vk = False
    
    if tg_chat_id:
        success_tg = post_to_telegram(bot, tg_chat_id, text, file_id, tags_str)
        debug_log("PUBLISH", f"Telegram: {'✅' if success_tg else '❌'}")
    
    if vk_token and vk_owner_id:
        success_vk, _ = post_to_vk(text, tags_str, vk_token, vk_owner_id, file_id)
        debug_log("PUBLISH", f"VK: {'✅' if success_vk else '❌'}")
    
    return success_tg or success_vk

def publish_delayed(bot, text, tags_str, delay_seconds, file_id=None):
    """Отложенная публикация"""
    time.sleep(delay_seconds)
    config = load_config()
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    publish_post_immediately(bot, tg_chat_id, text, tags_str, file_id)

def publish_from_pool(bot, vk_token, vk_owner_id, tg_chat_id):
    """Публикует один пост из пула и удаляет его"""
    pool = load_post_pool()
    if not pool:
        return False
    
    # Берём последний добавленный пост
    post = pool[-1]
    index = len(pool) - 1
    
    text = post.get("text", "")
    media_url = post.get("media_url")
    tags = build_tags(post)
    
    quote = get_random_quote()
    
    if len(text) < 100:
        description = generate_description(text)
        if description:
            text = f"{text}\n\n{description}"
    
    full_text = f"{text}\n\n📜 {quote}"
    
    success = False
    
    if tg_chat_id:
        try:
            if media_url:
                success_tg = post_to_telegram(bot, tg_chat_id, full_text, media_url, tags)
            else:
                theme_photo = get_theme_photo()
                if theme_photo:
                    success_tg = post_to_telegram(bot, tg_chat_id, full_text, theme_photo, tags)
                else:
                    success_tg = post_to_telegram(bot, tg_chat_id, full_text, None, tags)
            if success_tg:
                success = True
                debug_log("PUBLISH", f"Пост опубликован в Telegram")
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка Telegram: {e}", "ERROR")
    
    if vk_token and vk_owner_id:
        try:
            success_vk, _ = post_to_vk(full_text, tags, vk_token, vk_owner_id, media_url)
            if success_vk:
                success = True
                debug_log("PUBLISH", f"Пост опубликован в VK")
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка VK: {e}", "ERROR")
    
    # Удаляем пост из пула после публикации
    if success:
        remove_post_from_pool(index)
        debug_log("PUBLISH", f"Пост удалён из пула, осталось {len(load_post_pool())}")
    
    return success

def publish_loop(bot, vk_token, vk_owner_id, tg_chat_id):
    """Основной цикл автопостинга из пула"""
    debug_log("PUBLISH", "Цикл публикации запущен (лимит пула: 100)")
    
    while True:
        try:
            # Проверяем шаббат
            try:
                from dialogue.shabbat_manager import is_shabbat
                if is_shabbat():
                    debug_log("PUBLISH", "Шаббат — публикация отложена")
                    time.sleep(3600)
                    continue
            except ImportError:
                pass
            
            # Чистим пул если больше 100
            clean_pool()
            
            config = load_config()
            interval = config.get("publisher", {}).get("interval_seconds", 7200)
            
            published = publish_from_pool(bot, vk_token, vk_owner_id, tg_chat_id)
            
            if published:
                debug_log("PUBLISH", f"Опубликовано, следующая через {interval} сек")
            else:
                debug_log("PUBLISH", "Нет постов для публикации")
            
            time.sleep(interval)
            
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка в цикле: {e}", "ERROR")
            time.sleep(300)
