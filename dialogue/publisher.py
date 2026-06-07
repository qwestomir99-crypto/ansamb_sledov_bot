# ==========================================
# Файл: dialogue/publisher.py
# Справка: README.md → Публикатор
# Задача: публикация постов в TG и VK (немедленная, отложенная, из пула)
# Комментарий: VK — группа от имени пользователя
# ==========================================

import os
import json
import time
import random
import threading
from debug_utils import debug_log
from dialogue.publisher_utils import get_random_quote, get_auto_tags
from dialogue.post_manager import load_post_pool, save_post_pool, build_tags, remove_post_from_pool, add_post_to_pool

CONFIG_FILE = "config.json"
MAX_POOL_SIZE = 100

def load_config():
    with open(CONFIG_FILE, "r") as f: return json.load(f)

def clean_pool():
    pool = load_post_pool()
    if len(pool) > MAX_POOL_SIZE:
        pool = pool[-MAX_POOL_SIZE:]
        save_post_pool(pool)
        debug_log("PUBLISH", f"Пул очищен, оставлено {len(pool)} постов")

def publish_now_or_later(bot, user_id, text, tags, delay):
    if delay == 0:
        config = load_config()
        tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
        return publish_post_immediately(bot, tg_chat_id, text, " ".join(tags) if tags else "")
    else:
        return add_post_to_pool(text, tags, author=str(user_id))

def publish_post_immediately(bot, chat_id, text, tags_str=None, file_id=None):
    quote = get_random_quote()
    full_text = f"{text}\n\n📜 {quote}" if text else quote
    try:
        from services.photo_reader import get_random_post
        post = get_random_post()
        if post and post.get('photo_url'):
            bot.send_photo(chat_id, post['photo_url'], caption=full_text[:1024])
            return True
    except: pass
    try:
        auto_tags = get_auto_tags(full_text, "tg")
        if auto_tags: full_text = f"{full_text}\n\n{auto_tags}"
    except: pass
    try:
        bot.send_message(chat_id, full_text)
        return True
    except Exception as e:
        debug_log("PUBLISH", f"Ошибка: {e}", "ERROR")
        return False

def publish_from_pool(bot, vk_token, vk_owner_id, tg_chat_id):
    pool = load_post_pool()
    if not pool:
        try:
            from dialogue.content_mixer import publish_mixed_post
            return publish_mixed_post(bot, tg_chat_id)
        except ImportError: pass
        return False
    
    post = random.choice(pool)
    index = pool.index(post)
    full_text = f"{post.get('text', '')}\n\n📜 {get_random_quote()}"
    
    try:
        from services.photo_reader import get_random_post
        p = get_random_post()
        photo = p.get('photo_url') if p else None
    except: photo = None
    try:
        auto_tags = get_auto_tags(full_text, "tg")
        if auto_tags: full_text = f"{full_text}\n\n{auto_tags}"
    except: pass
    
    success = False
    if tg_chat_id:
        try:
            if photo: bot.send_photo(tg_chat_id, photo, caption=full_text[:1024])
            else: bot.send_message(tg_chat_id, full_text)
            success = True
        except Exception as e: debug_log("PUBLISH", f"Ошибка TG: {e}", "ERROR")
    
    vk_group_id = os.environ.get("VK_GROUP_ID")
    if vk_group_id:
        try:
            from services.app import get_vk_token
            token = get_vk_token()
            if token:
                from dialogue.publisher_utils import post_to_vk
                tags = build_tags(post)
                sv, _ = post_to_vk(full_text, tags, token, vk_group_id)
                if sv: success = True
        except Exception as e: debug_log("PUBLISH", f"Ошибка VK: {e}", "ERROR")
    
    if success: remove_post_from_pool(index)
    return success

def publish_loop(bot, vk_token, vk_owner_id, tg_chat_id):
    debug_log("PUBLISH", "Цикл публикации запущен (TG + VK группа)")
    while True:
        try:
            try:
                from dialogue.shabbat_manager import is_shabbat
                if is_shabbat(): time.sleep(3600); continue
            except ImportError: pass
            clean_pool()
            interval = load_config().get("publisher", {}).get("interval_seconds", 7200)
            if publish_from_pool(bot, vk_token, vk_owner_id, tg_chat_id):
                debug_log("PUBLISH", f"Опубликовано, следующая через {interval} сек")
            else: debug_log("PUBLISH", "Нет постов")
            time.sleep(interval)
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка: {e}", "ERROR")
            time.sleep(300)
