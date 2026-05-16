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

def add_publication(chat_id, text, delay_seconds, tags=None):
    pubs = load_publications()
    publish_at = time.time() + delay_seconds
    pubs.append({
        "id": len(pubs) + 1,
        "chat_id": chat_id,
        "text": text,
        "tags": tags,
        "publish_at": publish_at,
        "status": "pending"
    })
    save_publications(pubs)
    return True

def publish_loop(bot, vk_token, vk_owner_id, tg_chat_id):
    while True:
        now = time.time()
        pubs = load_publications()
        for pub in pubs:
            if pub["status"] == "pending" and pub["publish_at"] <= now:
                if pub["chat_id"] == "vk":
                    ok = post_to_vk(pub["text"], pub.get("tags", ""), vk_token, vk_owner_id)
                else:
                    ok = post_to_telegram(bot, tg_chat_id, pub["text"])
                if ok:
                    pub["status"] = "published"
                    pub["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_publications(pubs)
        time.sleep(30)
