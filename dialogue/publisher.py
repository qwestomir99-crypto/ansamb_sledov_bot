import time
import threading
import json
import os
from datetime import datetime
from dialogue.activity_modes import should_publish, get_current_mode_config
from dialogue.publisher_utils import post_to_telegram, post_to_vk
from dialogue.post_manager import get_post_for_publishing, build_tags, add_post_to_pool

PUBLICATIONS_FILE = "publications.json"

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

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
    text = post.get("text", "")
    tags = build_tags(post)
    full_message = f"{text}\n\n{tags}" if text else tags
    
    success_tg = False
    success_vk = False
    
    if platform in ["both", "telegram"]:
        try:
            success_tg = post_to_telegram(bot, tg_chat_id, text, None, tags)
            print(f"[PUBLISHER] Telegram: {'✅' if success_tg else '❌'}")
        except Exception as e:
            print(f"[PUBLISHER] Telegram ошибка: {e}")
    
    if platform in ["both", "vk"] and vk_token and vk_owner_id:
        try:
            success_vk = post_to_vk(text, tags, vk_token, vk_owner_id, None)
            print(f"[PUBLISHER] VK: {'✅' if success_vk else '❌'}")
        except Exception as e:
            print(f"[PUBLISHER] VK ошибка: {e}")
    
    return success_tg or success_vk

def publish_loop(bot, vk_token, vk_owner_id, tg_chat_id):
    print("[PUBLISHER] Поток публикатора запущен, проверка каждые 30 секунд")
    
    last_pool_check = 0
    last_interval = None
    
    while True:
        try:
            # Получаем интервал из текущего режима
            mode_config = get_current_mode_config()
            pool_interval = mode_config.get("publisher_interval", 0)
            
            # Если интервал изменился или ещё не установлен
            if pool_interval != last_interval:
                last_interval = pool_interval
                if pool_interval > 0:
                    print(f"[PUBLISHER] Интервал публикаций обновлён: {pool_interval} минут")
                else:
                    print("[PUBLISHER] Публикации отключены в текущем режиме")
            
            # Проверяем, можно ли публиковать по режиму
            if not should_publish() or pool_interval <= 0:
                time.sleep(30)
                continue
            
            # Обрабатываем отложенные публикации
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
            
            # Публикуем пост из пула с интервалом из режима
            current_time = time.time()
            interval_seconds = pool_interval * 60
            
            if current_time - last_pool_check >= interval_seconds:
                last_pool_check = current_time
                
                post, index = get_post_for_publishing()
                if post:
                    print(f"[PUBLISHER] Публикуем пост из пула (интервал {pool_interval} мин)")
                    publish_post(bot, tg_chat_id, vk_token, vk_owner_id, post)
                else:
                    print("[PUBLISHER] Нет постов в пуле")
            
        except Exception as e:
            print(f"[PUBLISHER] Ошибка в цикле: {e}")
        
        time.sleep(30)
