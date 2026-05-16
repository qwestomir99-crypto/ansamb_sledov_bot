import time
import threading
import json
import os
from datetime import datetime
from dialogue.activity_modes import should_publish
from dialogue.publisher_utils import post_to_telegram, post_to_vk

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

def publish_loop(bot, vk_token, vk_owner_id, tg_chat_id):
    print("[PUBLISHER] Поток публикатора запущен, проверка каждые 30 секунд")
    
    while True:
        try:
            # Проверяем, можно ли публиковать по режиму
            if not should_publish():
                time.sleep(30)
                continue
            
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
                        print(f"[PUBLISHER] Опубликовано в {platform}: {text[:50] if text else '[без текста]'}...")
                    else:
                        print(f"[PUBLISHER] Ошибка публикации в {platform}")
                    
                    # Не удаляем, а помечаем как опубликованное
                    time.sleep(1)
            
            if changed:
                save_publications(pubs)
            
            # Очистка старых опубликованных записей (старше 24 часов)
            cleaned = False
            new_pubs = []
            for pub in pubs:
                if pub["status"] == "published":
                    if pub.get("published_at", 0) < now - 86400:  # 24 часа
                        cleaned = True
                        continue
                new_pubs.append(pub)
            
            if cleaned:
                save_publications(new_pubs)
            
        except Exception as e:
            print(f"[PUBLISHER] Ошибка в цикле: {e}")
        
        time.sleep(30)
