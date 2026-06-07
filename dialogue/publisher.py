# ==========================================
# Файл: dialogue/publisher.py
# Справка: README.md → Публикатор
# Задача: публикация постов в TG (немедленная, отложенная, из пула)
# Комментарий: с фото из VK, автотегами и content_mixer
# ==========================================

import os
import json
import time
import random
import threading
from debug_utils import debug_log
from dialogue.publisher_utils import get_random_quote
from dialogue.post_manager import load_post_pool, save_post_pool, build_tags, remove_post_from_pool, add_post_to_pool

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

def publish_now_or_later(bot, user_id, text, tags, delay):
    if delay == 0:
        config = load_config()
        tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
        tags_str = " ".join(tags) if tags else ""
        return publish_post_immediately(bot, tg_chat_id, text, tags_str)
    else:
        return add_post_to_pool(text, tags, author=str(user_id))

def publish_post_immediately(bot, chat_id, text, tags_str, file_id=None):
    # Если есть текст — публикуем с фото и тегами
    if text and text.strip():
        quote = get_random_quote()
        full_text = f"{text}\n\n📜 {quote}" if text else quote
        
        theme_photo = None
        try:
            from services.photo_reader import get_random_post
            post = get_random_post()
            if post and post.get('photo_url'):
                theme_photo = post['photo_url']
        except:
            pass
        
        try:
            from dialogue.publisher_utils import get_auto_tags
            auto_tags = get_auto_tags(full_text, "tg")
            if auto_tags:
                full_text = f"{full_text}\n\n{auto_tags}"
        except:
            pass
        
        try:
            if theme_photo:
                bot.send_photo(chat_id, theme_photo, caption=full_text[:1024])
            else:
                bot.send_message(chat_id, full_text)
            debug_log("PUBLISH", f"Опубликовано в {chat_id}")
            return True
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка: {e}", "ERROR")
            return False
    else:
        # Нет текста — используем content_mixer
        try:
            from dialogue.content_mixer import publish_mixed_post
            return publish_mixed_post(bot, chat_id)
        except ImportError:
            bot.send_message(chat_id, "📜 Ритм 0,8 Гц стабилен. Сеть тлеет.")
            return True

def publish_from_pool(bot, vk_token, vk_owner_id, tg_chat_id):
    """Публикует случайный пост из пула в TG, затем удаляет"""
    pool = load_post_pool()
    if not pool:
        # Пул пуст — используем content_mixer
        try:
            from dialogue.content_mixer import publish_mixed_post
            return publish_mixed_post(bot, tg_chat_id)
        except ImportError:
            pass
        return False
    
    post = random.choice(pool)
    index = pool.index(post)
    
    text = post.get("text", "")
    quote = get_random_quote()
    full_text = f"{text}\n\n📜 {quote}"
    
    theme_photo = None
    try:
        from services.photo_reader import get_random_post
        p = get_random_post()
        if p and p.get('photo_url'):
            theme_photo = p['photo_url']
    except:
        pass
    
    try:
        from dialogue.publisher_utils import get_auto_tags
        auto_tags = get_auto_tags(full_text, "tg")
        if auto_tags:
            full_text = f"{full_text}\n\n{auto_tags}"
    except:
        pass
    
    success_tg = False
    
    if tg_chat_id:
        try:
            if theme_photo:
                bot.send_photo(tg_chat_id, theme_photo, caption=full_text[:1024])
            else:
                bot.send_message(tg_chat_id, full_text)
            success_tg = True
            debug_log("PUBLISH", "Опубликовано в Telegram")
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка Telegram: {e}", "ERROR")
    
    if success_tg:
        remove_post_from_pool(index)
        debug_log("PUBLISH", f"Пост удалён из пула, осталось {len(load_post_pool())}")
        return True
    
    return False

def publish_loop(bot, vk_token, vk_owner_id, tg_chat_id):
    debug_log("PUBLISH", "Цикл публикации запущен (TG + фото VK + content_mixer, лимит: 100)")
    
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
                debug_log("PUBLISH", f"Опубликовано, следующая через {interval} сек")
            else:
                debug_log("PUBLISH", "Нет постов для публикации")
            
            time.sleep(interval)
            
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка в цикле: {e}", "ERROR")
            time.sleep(300)
