import time
import threading
import json
import os
from datetime import datetime
from dialogue.activity_modes import should_publish
from dialogue.publisher_utils import post_to_telegram, post_to_vk
from dialogue.post_manager import get_post_for_publishing, build_tags, add_post_to_pool

PUBLICATIONS_FILE = "publications.json"
CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def load_publications():
    if not os.path.exists(PUBLICATIONS_FILE):
        return []
    with open(PUBLICATIONS_FILE, "r") as f:
        return json.load(f)

def save_publications(pubs):
    with open(PUBLICATIONS_FILE, "w") as f:
        json.dump(pubs, f, indent=2)

def add_publication(platform, text, delay_seconds, tags, file_path=None):
    pubs = load_publications()
    publish_at = time.time() + delay_seconds
    pubs.append({
        "platform": platform,
        "text": text,
        "publish_at": publish_at,
        "tags": tags,
        "file_path": file_path,
        "status": "pending"
    })
    save_publications(pubs)

def publish_post(bot, tg_chat_id, vk_token, vk_owner_id, post, platform="both"):
    """
    Публикует один пост в Telegram и/или VK
    """
    text = post.get("text", "")
    tags = build_tags(post)
    full_message = f"{text}\n\n{tags}" if text else tags
    
    success_tg = False
    success_vk = False
    
    # Telegram
    if platform in ["both", "telegram"]:
        try:
            success_tg = post_to_telegram(bot, tg_chat_id, text, None, tags)
            print(f"[PUBLISHER] Telegram: {'✅' if success_tg else '❌'}")
        except Exception as e:
            print(f"[PUBLISHER] Telegram ошибка: {e}")
    
    # VK
    if platform in ["both", "vk"] and vk_token and vk_owner_id:
        try:
            success_vk = post_to_vk(text, tags, vk_token, vk_owner_id, None)
            print(f"[PUBLISHER] VK: {'✅' if success_vk else '❌'}")
        except Exception as e:
            print(f"[PUBLISHER] VK ошибка: {e}")
    
    return success_tg or success_vk

def publish_loop(bot, vk_token, vk_owner_id, tg_chat_id):
    """
    Основной цикл публикатора.
    Проверяет отложенные публикации и публикует посты из post_pool.
    """
    print("[PUBLISHER] Поток публикатора запущен, проверка каждые 30 секунд")
    
    last_pool_check = 0
    pool_interval = 3600  # Проверяем пул раз в час (можно настроить)
    
    while True:
        try:
            # Проверяем, можно ли публиковать по режиму
            if not should_publish():
                time.sleep(30)
                continue
            
            # 1. Обрабатываем отложенные публикации
            pubs = load_publications()
            now = time.time()
            changed = False
            
            for pub in pubs[:]:
                if pub.get("status") != "pending":
                    continue
                
                if pub["publish_at"] <= now:
                    platform = pub["platform"]
                    text = pub.get("text")
                    tags = pub.get("tags", "")
                    file_path = pub.get("file_path")
                    
                    success = False
                    
                    if platform == "telegram":
                        success = post_to_telegram(bot, tg_chat_id, text, file_path, tags)
                    elif platform == "vk":
                        success = post_to_vk(text, tags, vk_token, vk_owner_id, file_path)
                    
                    if success:
                        pub["status"] = "published"
                        pub["published_at"] = now
                        changed = True
                        print(f"[PUBLISHER] Отложенный пост опубликован")
                    
                    time.sleep(1)
            
            if changed:
                save_publications(pubs)
            
            # Очистка старых опубликованных записей (старше 24 часов)
            cleaned = False
            new_pubs = []
            for pub in pubs:
                if pub["status"] == "published":
                    if pub.get("published_at", 0) < now - 86400:
                        cleaned = True
                        continue
                new_pubs.append(pub)
            
            if cleaned:
                save_publications(new_pubs)
            
            # 2. Публикуем пост из post_pool (раз в час или по расписанию)
            current_time = time.time()
            if current_time - last_pool_check >= pool_interval:
                last_pool_check = current_time
                
                post, index = get_post_for_publishing()
                if post:
                    print(f"[PUBLISHER] Публикуем пост из пула (индекс {index})")
                    publish_post(bot, tg_chat_id, vk_token, vk_owner_id, post)
                else:
                    print("[PUBLISHER] Нет постов в пуле")
            
        except Exception as e:
            print(f"[PUBLISHER] Ошибка в цикле: {e}")
        
        time.sleep(30)
