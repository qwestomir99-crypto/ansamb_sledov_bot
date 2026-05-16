import json
import time
import threading
from datetime import datetime
from dialogue.publisher_utils import post_to_telegram, post_to_vk

CONFIG_FILE = "config.json"
PUBLICATIONS_FILE = "publications.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

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
        "id": len(pubs),
        "chat_id": chat_id,
        "text": text,
        "tags": tags,
        "publish_at": publish_at,
        "status": "pending"
    })
    save_publications(pubs)
    return True

def publish_loop(bot, vk_token, vk_owner_id, tg_channel_id):
    while True:
        now = time.time()
        pubs = load_publications()
        for pub in pubs:
            if pub["status"] == "pending" and pub["publish_at"] <= now:
                if pub["chat_id"] == "vk":
                    ok = post_to_vk(pub["text"], pub.get("tags", ""), vk_token, vk_owner_id)
                else:
                    ok = post_to_telegram(bot, pub["chat_id"], pub["text"])
                if ok:
                    pub["status"] = "published"
                    pub["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_publications(pubs)
        time.sleep(30)
