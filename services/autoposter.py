# ==========================================
# Модуль: services/autoposter.py
# Справка: README.md → Автопостинг
# Задача: пересылка сообщений из группы в канал и VK через Userbot
# Комментарий: поддерживает файлы до 2 ГБ, не использует Bot API для больших видео
# Зависит от: config.json, publisher_utils.py
# Вызывается из: bot.py, admin_commands.py (upload_via_userbot)
# ==========================================

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

# Данные для Userbot (берутся из переменных окружения)
API_ID = int(os.environ.get("TG_API_ID", 0))
API_HASH = os.environ.get("TG_API_HASH", "")
PHONE = os.environ.get("TG_PHONE_NUMBER", "")

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

def get_vk_upload_url(vk_token, owner_id):
    params = {
        "access_token": vk_token,
        "v": "5.199",
        "owner_id": owner_id
    }
    try:
        r = requests.get("https://api.vk.com/method/photos.getWallUploadServer", params=params, timeout=10)
        data = r.json()
        return data.get("response", {}).get("upload_url")
    except Exception as e:
        print(f"[VK] upload URL ошибка: {e}")
        return None

def upload_photo_to_vk(upload_url, file_path, vk_token):
    try:
        with open(file_path, 'rb') as f:
            files = {'photo': f}
            r = requests.post(upload_url, files=files)
            data = r.json()
        save_params = {
            "access_token": vk_token,
            "v": "5.199",
            "photo": data['photo'],
            "server": data['server'],
            "hash": data['hash']
        }
        r = requests.get("https://api.vk.com/method/photos.saveWallPhoto", params=save_params)
        photo_data = r.json()
        if 'response' in photo_data and photo_data['response']:
            photo = photo_data['response'][0]
            return f"photo{photo['owner_id']}_{photo['id']}"
        else:
            print(f"[VK] save photo ошибка: {photo_data}")
            return None
    except Exception as e:
        print(f"[VK] upload photo ошибка: {e}")
        return None

def send_to_vk(text, post, vk_token, vk_owner_id, file_path=None):
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
    if file_path and os.path.exists(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            upload_url = get_vk_upload_url(vk_token, vk_owner_id)
            if upload_url:
                photo_attachment = upload_photo_to_vk(upload_url, file_path, vk_token)
                if photo_attachment:
                    params['attachments'] = photo_attachment
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            print(f"[VK] Видео пока не поддерживается, публикуем только текст")
    try:
        r = requests.post("https://api.vk.com/method/wall.post", params=params, timeout=10)
        if r.json().get("response"):
            print(f"[VK] ✅ отправлено: {tags[:50]}...")
        else:
            print(f"[VK] ошибка: {r.json()}")
    except Exception as e:
        print(f"[VK] исключение: {e}")

# ==========================================
# Функция для загрузки больших файлов через Userbot
# Вызывается из admin_commands.py
# ==========================================

async def upload_via_userbot_async(file_id, caption, tags, vk_token, vk_owner_id, message):
    """Загружает файл через Userbot (Telethon) и отправляет в VK"""
    if not API_ID or not API_HASH or not PHONE:
        print("[USERBOT] Не настроены TG_API_ID/TG_API_HASH/TG_PHONE_NUMBER")
        return False
    
    client = TelegramClient("autoposter_session", API_ID, API_HASH)
    await client.start(phone=PHONE)
    
    try:
        # Скачиваем файл из Telegram по message (Telethon умеет сам)
        print(f"[USERBOT] Скачивание файла...")
        file_path = await client.download_media(message)
        if not file_path:
            print("[USERBOT] Не удалось скачать файл")
            return False
        
        file_size = os.path.getsize(file_path)
        print(f"[USERBOT] Файл скачан: {file_path}, размер: {file_size / 1024 / 1024:.1f} МБ")
        
        # Подготавливаем пост
        full_text = f"{caption}\n\n{tags}"
        
        # Отправляем в VK
        params = {
            "access_token": vk_token,
            "v": "5.199",
            "owner_id": vk_owner_id,
            "message": full_text,
            "from_group": 1
        }
        
        # Пытаемся прикрепить файл (если это фото)
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            upload_url = get_vk_upload_url(vk_token, vk_owner_id)
            if upload_url:
                photo_attachment = upload_photo_to_vk(upload_url, file_path, vk_token)
                if photo_attachment:
                    params['attachments'] = photo_attachment
                    print("[USERBOT] Фото прикреплено")
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            # Видео через Userbot: VK API не поддерживает прямую загрузку, публикуем ссылку
            print("[USERBOT] Видео публикуется без прикрепления (VK API ограничен)")
        
        r = requests.post("https://api.vk.com/method/wall.post", params=params, timeout=30)
        data = r.json()
        
        if 'response' in data:
            print(f"[USERBOT] ✅ Пост отправлен в VK")
            success = True
        else:
            print(f"[USERBOT] ❌ Ошибка VK: {data}")
            success = False
        
        # Удаляем временный файл
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"[USERBOT] Временный файл удалён")
        
        return success
        
    except Exception as e:
        print(f"[USERBOT] Ошибка: {e}")
        return False
    finally:
        await client.disconnect()

def upload_via_userbot(file_id, caption, tags, vk_token, vk_owner_id, message):
    """Синхронная обёртка для вызова из admin_commands.py"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(upload_via_userbot_async(file_id, caption, tags, vk_token, vk_owner_id, message))

# ==========================================
# Основной поток автопостинга (отключён)
# ==========================================

def start_autoposter(config, vk_token, vk_owner_id):
    ap_config = config.get("autoposter", {})
    if not ap_config.get("enabled"):
        print("[AUTOPOSTER] Отключën в конфиге")
        return

    source_chat_id = int(ap_config.get("source_chat_id"))
    target_chat_id = ap_config.get("target_chat_id")

    if not source_chat_id or not target_chat_id:
        print("[AUTOPOSTER] Ошибка: не хватает настроек в конфиге")
        return

    if not API_ID or not API_HASH or not PHONE:
        print("[AUTOPOSTER] Ошибка: нет TG_API_ID/TG_API_HASH/TG_PHONE_NUMBER")
        return

    async def run():
        client = TelegramClient("autoposter_session", API_ID, API_HASH)

        @client.on(events.NewMessage(chats=source_chat_id))
        async def handler(event):
            message = event.message
            sender = await event.get_sender()
            
            if sender.bot:
                print(f"[AUTOPOSTER] Игнор: сообщение от бота {sender.id}")
                return
            
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
            
            if not message.text and not message.media:
                return
            
            text = message.text or "Медиа-пост"
            print(f"[AUTOPOSTER] Перехвачено: {text[:50]}...")
            
            post = find_or_create_post(text, sender.id)
            
            # Telegram канал (с эмодзи 🔁)
            try:
                tg_tags = build_tg_tags(post)
                if message.media:
                    await client.send_file(target_chat_id, message.media, caption=f"🔁 {text}\n\n{tg_tags}")
                else:
                    await client.send_message(target_chat_id, f"🔁 {text}\n\n{tg_tags}")
                print(f"[AUTOPOSTER] ✅ Telegram")
            except Exception as e:
                print(f"[AUTOPOSTER] ❌ Telegram: {e}")
            
            # VK (если есть токен)
            if vk_token and vk_owner_id:
                send_to_vk(text, post, vk_token, vk_owner_id)

        await client.start(phone=PHONE)
        print(f"[AUTOPOSTER] ✅ Мониторинг запущен. Слушаю чат {source_chat_id} → {target_chat_id}")
        await client.run_until_disconnected()

    def start_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run())

    threading.Thread(target=start_loop, daemon=True).start()
    print("[AUTOPOSTER] Поток запущен")
