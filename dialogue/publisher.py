import json
import time
import os
from datetime import datetime
from dialogue.publisher_utils import post_to_telegram, post_to_vk

PUBLICATIONS_FILE = "publications.json"

def load_publications():
    if not os.path.exists(PUBLICATIONS_FILE):
        return []
    with open(PUBLICATIONS_FILE, "r") as f:
        return json.load(f)

def save_publications(pubs):
    with open(PUBLICATIONS_FILE, "w") as f:
        json.dump(pubs, f, indent=2)

def add_publication(chat_id, text, delay_seconds, tags=None, file_path=None):
    pubs = load_publications()
    publish_at = time.time() + delay_seconds
    new_id = len(pubs) + 1
    new_pub = {
        "id": new_id,
        "chat_id": chat_id,
        "text": text or "",
        "tags": tags,
        "file_path": file_path,
        "publish_at": publish_at,
        "status": "pending"
    }
    pubs.append(new_pub)
    save_publications(pubs)
    print(f"[PUBLISHER] Добавлена публикация #{new_id} через {delay_seconds} сек, текст: {bool(text)}, файл: {bool(file_path)}")
    return True

def publish_loop(bot, vk_token, vk_owner_id, tg_chat_id):
    print("[PUBLISHER] Поток публикатора запущен, проверка каждые 30 секунд")
    while True:
        try:
            now = time.time()
            pubs = load_publications()
            changed = False
            
            for pub in pubs:
                if pub["status"] == "pending" and pub["publish_at"] <= now:
                    print(f"[PUBLISHER] Публикую #{pub['id']}: текст={bool(pub['text'])}, файл={bool(pub.get('file_path'))}")
                    
                    if pub["chat_id"] == "vk":
                        ok = post_to_vk(
                            pub["text"], 
                            pub.get("tags", ""), 
                            vk_token, 
                            vk_owner_id, 
                            pub.get("file_path")
                        )
                    else:
                        ok = post_to_telegram(
                            bot, 
                            tg_chat_id, 
                            pub["text"], 
                            pub.get("file_path"), 
                            pub.get("tags")
                        )
                    
                    if ok:
                        pub["status"] = "published"
                        pub["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        changed = True
                        print(f"[PUBLISHER] Публикация #{pub['id']} успешна")
                    else:
                        print(f"[PUBLISHER] Ошибка публикации #{pub['id']}")
            
            if changed:
                save_publications(pubs)
                
        except Exception as e:
            print(f"[PUBLISHER] Ошибка в цикле: {e}")
        
        time.sleep(30)
