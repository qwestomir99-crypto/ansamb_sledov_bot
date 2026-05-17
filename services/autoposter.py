import asyncio
import os
import json
import requests
import threading
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat, ChannelParticipantsAdmins

POST_POOL_FILE = "dialogue/data/post_pool.json"
CONFIG_FILE = "config.json"

def load_post_pool():
    if not os.path.exists(POST_POOL_FILE):
        return []
    with open(POST_POOL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_post_pool(pool):
    with open(POST_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(pool, f, indent=2, ensure_ascii=False)

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def find_or_create_post(text, admin_user_id):
    pool = load_post_pool()
    for post in pool:
        if post.get("text") == text:
            return post

    cfg = load_config()
    default_tags = cfg.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")

    new_post = {
        "text": text,
        "tags": default_tags.split(),
        "author": str(admin_user_id),
        "weight": 50,
        "added": datetime.now().strftime("%Y-%m-%d"),
        "last_posted": None,
        "source": "autoposter"
    }
    pool.append(new_post)
    save_post_pool(pool)
    print(f"[AUTOPOSTER] 📝 Добавлен новый пост: {text[:50]}...")
    return new_post

def build_tg_tags(post):
    cfg = load_config()
    tags = set()
    default_tags = cfg.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")
    tags.update(default_tags.split())
    tags.update(post.get("tags", []))
    author = post.get("author", "")
    if author and author != "unknown":
        tags.add(f"#{author}")
    return " ".join(tags)

def build_vk_tags(post):
    cfg = load_config()
    tags = set()
    vk_tags = cfg.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
    tags.update(vk_tags.split())
    extra_tags = post.get("tags", [])
    default_tags = cfg.get("publisher", {}).get("default_tags", "").split()
    for t in extra_tags:
        if t not in default_tags:
            tags.add(t)
    return " ".join(tags)

def send_to_vk(text, post, vk_token, vk_owner_id):
    if not vk_token or not vk_owner_id:
        return
    tags = build_vk_tags(post)
    full_text = f"{text}\n\n{tags}"
    params = {
        "access_token": vk_token,
        "v": "5.199",
        "owner_id": vk_owner_id,
        "message": full_text,
        "from_group": 1
    }
    try:
        r = requests.post("https://api.vk.com/method/wall.post", params=params, timeout=10)
        if r.json().get("response"):
            print(f"[VK] ✅ отправлено: {tags[:50]}...")
        else:
            print(f"[VK] ошибка: {r.json()}")
    except Exception as e:
        print(f"[VK] исключение: {e}")

def start_autoposter(config, vk_token, vk_owner_id):
    ap_config = config.get("autoposter", {})
    if not ap_config.get("enabled"):
        print("[AUTOPOSTER] Отключён в конфиге")
        return

    source_chat_id = int(ap_config.get("source_chat_id"))
    target_chat_id = ap_config.get("target_chat_id")

    if not source_chat_id or not target_chat_id:
        print("[AUTOPOSTER] Ошибка: не хватает настроек в конфиге")
        return

    api_id = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    phone = os.environ.get("TG_PHONE_NUMBER")

    if not api_id or not api_hash or not phone:
        print("[AUTOPOSTER] Ошибка: нет TG_API_ID/TG_API_HASH/TG_PHONE_NUMBER")
        return

    api_id = int(api_id)

    async def run():
        client = TelegramClient("autoposter_session", api_id, api_hash)

        @client.on(events.NewMessage(chats=source_chat_id))
        async def handler(event):
            message = event.message
            sender = await event.get_sender()
            
            # Игнорируем ботов
            if sender.bot:
                print(f"[AUTOPOSTER] Игнор: сообщение от бота {sender.id}")
                return
            
            # Проверяем, является ли отправитель администратором группы
            try:
                chat = await event.get_chat()
                if not isinstance(chat, (Channel, Chat)):
                    return
                
                is_admin = False
                async for user in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
                    if user.id == sender.id:
                        is_admin = True
                        break
                
                if not is_admin:
                    print(f"[AUTOPOSTER] Игнор: {sender.id} не администратор")
                    return
                    
                print(f"[AUTOPOSTER] ✅ Сообщение от администратора {sender.id}")
                
            except Exception as e:
                print(f"[AUTOPOSTER] Ошибка проверки прав: {e}")
                return
            
            if not message.text:
                return
            
            text = message.text.strip()
            print(f"[AUTOPOSTER] Перехвачено: {text[:50]}...")
            
            post = find_or_create_post(text, sender.id)
            
            # Telegram канал
            try:
                tg_tags = build_tg_tags(post)
                await client.send_message(target_chat_id, f"{text}\n\n{tg_tags}")
                print(f"[AUTOPOSTER] ✅ Telegram")
            except Exception as e:
                print(f"[AUTOPOSTER] ❌ Telegram: {e}")
            
            # VK
            send_to_vk(text, post, vk_token, vk_owner_id)

        await client.start(phone=phone)
        print(f"[AUTOPOSTER] ✅ Мониторинг запущен. Слушаю чат {source_chat_id} → {target_chat_id}")
        await client.run_until_disconnected()

    def start_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run())

    threading.Thread(target=start_loop, daemon=True).start()
    print("[AUTOPOSTER] Поток запущен")
