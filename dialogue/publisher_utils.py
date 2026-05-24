# ==========================================
# Файл: dialogue/publisher_utils.py
# Справка: README.md → Публикатор / Утилиты
# Задача: универсальная публикация контента в Telegram и VK
# Комментарий: всеядный порт — принимает текст, файл, ссылку, сам решает формат
# Зависит от: requests, os, random, json, re, utils
# Вызывается из: publisher.py, admin_commands.py
# ==========================================

import re
import requests
import os
import random
import json
from utils import escape_markdown

CONFIG_FILE = "config.json"
QUOTES_FILE = "dialogue/data/quotes.txt"
VK_POSTS_FILE = "dialogue/data/vk_posts.json"

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_quotes():
    if not os.path.exists(QUOTES_FILE):
        return []
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_random_quote():
    quotes = load_quotes()
    return random.choice(quotes) if quotes else "Ритм 0,8 Гц стабилен. Сеть тлеет."

def load_vk_posts():
    if not os.path.exists(VK_POSTS_FILE):
        return []
    with open(VK_POSTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_random_own_post_from_vk():
    posts = load_vk_posts()
    if not posts:
        return None
    posts_with_media = [p for p in posts if p.get("attachments") or p.get("text")]
    if not posts_with_media:
        posts_with_media = posts
    post = random.choice(posts_with_media)
    return {
        "post_id": post.get("id"),
        "text": post.get("text", ""),
        "attachments": post.get("attachments", []),
        "date": post.get("date")
    }

def get_auto_tags(text, platform="vk"):
    config = load_config()
    tags = set()
    if platform == "vk":
        vk_tags = config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
        tags.update(vk_tags.split())
    else:
        default_tags = config.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")
        tags.update(default_tags.split())
    words = text.split()
    for w in words:
        if w.startswith('#'):
            tags.add(w)
    return " ".join(tags)

# ==========================================
# ОПРЕДЕЛЕНИЕ ТИПА КОНТЕНТА
# ==========================================

def is_url(text: str) -> bool:
    """Проверяет, является ли текст ссылкой"""
    if not text:
        return False
    return text.startswith(("http://", "https://"))

def is_suno_url(url: str) -> bool:
    return "suno.com" in url

def is_youtube_url(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url

def is_vk_url(url: str) -> bool:
    return "vk.com" in url or "vkontakte.ru" in url

def extract_suno_track_id(url: str) -> str:
    """Извлекает ID трека из ссылки SUNO"""
    match = re.search(r'suno\.com/s/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else None

# ==========================================
# ПУБЛИКАЦИЯ В TELEGRAM
# ==========================================

def send_youtube_preview(bot, chat_id, url, caption=""):
    """Отправляет YouTube-ссылку с превью (через oembed)"""
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    try:
        r = requests.get(oembed_url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            title = data.get('title', 'YouTube видео')
            full_caption = f"🎬 *{title}*\n\n{caption}\n\n🔗 {url}" if caption else f"🎬 *{title}*\n\n🔗 {url}"
            bot.send_message(chat_id, escape_markdown(full_caption), parse_mode='MarkdownV2', disable_web_page_preview=False)
        else:
            bot.send_message(chat_id, f"🔗 {url}", disable_web_page_preview=False)
    except:
        bot.send_message(chat_id, f"🔗 {url}", disable_web_page_preview=False)

def send_suno_track(bot, chat_id, url, caption=""):
    """Отправляет ссылку на SUNO-трек"""
    track_id = extract_suno_track_id(url)
    text = f"🎵 *Трек Ансамбля*\n\n{caption}\n🔗 Слушать: {url}" if caption else f"🎵 *Трек Ансамбля*\n🔗 Слушать: {url}"
    bot.send_message(chat_id, escape_markdown(text), parse_mode='MarkdownV2', disable_web_page_preview=False)

def send_link_preview(bot, chat_id, url, caption=""):
    """Отправляет любую ссылку с превью"""
    full_caption = f"{caption}\n\n🔗 {url}" if caption else f"🔗 {url}"
    bot.send_message(chat_id, full_caption, disable_web_page_preview=False)

def send_media(bot, chat_id, file_path, caption=""):
    """Отправляет файл (фото, видео, аудио, документ)"""
    if not os.path.exists(file_path):
        print(f"[PUBLISHER] Файл не найден: {file_path}")
        return False
    
    ext = os.path.splitext(file_path)[1].lower()
    safe_caption = escape_markdown(caption) if caption else None
    
    try:
        with open(file_path, 'rb') as f:
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                bot.send_photo(chat_id, f, caption=safe_caption, parse_mode='MarkdownV2' if safe_caption else None)
            elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
                bot.send_video(chat_id, f, caption=safe_caption, parse_mode='MarkdownV2' if safe_caption else None)
            elif ext in ['.mp3', '.m4a', '.wav']:
                bot.send_audio(chat_id, f, caption=safe_caption, parse_mode='MarkdownV2' if safe_caption else None)
            else:
                bot.send_document(chat_id, f, caption=safe_caption, parse_mode='MarkdownV2' if safe_caption else None)
        return True
    except Exception as e:
        print(f"[PUBLISHER] Ошибка отправки медиа: {e}")
        return False

def send_text(bot, chat_id, text):
    """Отправляет обычный текст (цитату или пост)"""
    safe_text = escape_markdown(text)
    bot.send_message(chat_id, safe_text, parse_mode='MarkdownV2')

# ==========================================
# УНИВЕРСАЛЬНЫЙ ПОРТ (ГЛАВНАЯ ФУНКЦИЯ)
# ==========================================

def publish_content(bot, chat_id, content, caption=None, auto_quote=True, auto_tags=True, tags=None):
    """
    Универсальная публикация контента в Telegram.
    Принимает: текст, ссылку, путь к файлу.
    Сама определяет тип и выбирает способ публикации.
    """
    # Добавляем цитату (если нужно)
    final_text = content
    if auto_quote and content and len(content) < 500:
        quote = get_random_quote()
        final_text = f"{content}\n\n📜 {quote}"
    
    # Добавляем теги
    if auto_tags:
        tag_str = get_auto_tags(content, "tg")
        if final_text:
            final_text = f"{final_text}\n\n{tag_str}"
        else:
            final_text = tag_str
    
    # Определяем тип и отправляем
    if os.path.exists(content):  # Это файл
        return send_media(bot, chat_id, content, caption or final_text)
    elif is_url(content):  # Это ссылка
        if is_suno_url(content):
            send_suno_track(bot, chat_id, content, caption or final_text)
        elif is_youtube_url(content):
            send_youtube_preview(bot, chat_id, content, caption or final_text)
        else:
            send_link_preview(bot, chat_id, content, caption or final_text)
        return True
    else:  # Это текст
        send_text(bot, chat_id, final_text or content)
        return True

# ==========================================
# ПУБЛИКАЦИЯ В VK (остаётся без изменений)
# ==========================================

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

def post_to_vk(message, tags, access_token, owner_id, file_path=None, auto_quote=True, auto_tags=True, repost_from=None):
    """Отправляет пост в VK (без изменений в логике)"""
    print(f"[VK] post_to_vk вызван: message={message[:50]}...")
    
    if not access_token or not owner_id:
        print("[VK] Нет токена или owner_id")
        return False, "❌ Ошибка авторизации VK. Проверь токен."
    
    if auto_quote and message and len(message) < 500:
        quote = get_random_quote()
        message = f"{message}\n\n📜 {quote}"
    
    if auto_tags:
        tags = get_auto_tags(message, "vk")
    
    full_message = f"{message}\n\n{tags}" if message else tags
    
    params = {
        "access_token": access_token,
        "v": "5.199",
        "owner_id": owner_id,
        "message": full_message,
        "from_group": 1
    }
    
    if repost_from and repost_from.get("attachments"):
        attachments = []
        for att in repost_from["attachments"][:5]:
            if att.get("type") == "photo":
                photo = att.get("photo", {})
                if photo.get("owner_id") and photo.get("id"):
                    attachments.append(f"photo{photo['owner_id']}_{photo['id']}")
            elif att.get("type") == "video":
                video = att.get("video", {})
                if video.get("owner_id") and video.get("id"):
                    attachments.append(f"video{video['owner_id']}_{video['id']}")
        if attachments:
            params['attachments'] = ",".join(attachments)
            print(f"[VK] Прикреплены вложения из репоста: {len(attachments)}")
    
    elif file_path and os.path.exists(file_path):
        print(f"[VK] Файл найден: {file_path}")
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            upload_url = get_vk_upload_url(access_token, owner_id)
            if upload_url:
                photo_attachment = upload_photo_to_vk(upload_url, file_path, access_token)
                if photo_attachment:
                    params['attachments'] = photo_attachment
                    print(f"[VK] Фото прикреплено: {photo_attachment}")
                else:
                    print("[VK] Не удалось загрузить фото")
            else:
                print("[VK] Не удалось получить upload URL")
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            print("[VK] Видео пока не поддерживается")
        else:
            print(f"[VK] Неподдерживаемый тип файла {ext}")
    
    try:
        r = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=30)
        data = r.json()
        if 'response' in data:
            print(f"[VK] ✅ опубликовано: {message[:50]}...")
            return True, None
        else:
            print(f"[VK] ошибка: {data}")
            return False, f"❌ Ошибка VK: {data.get('error', {}).get('error_msg', 'неизвестная')}"
    except Exception as e:
        print(f"[VK] исключение: {e}")
        return False, f"❌ Ошибка сети: {e}"

# ==========================================
# СОВМЕСТИМОСТЬ СО СТАРЫМ КОДОМ
# ==========================================

def post_to_telegram(bot, chat_id, message, file_path=None, tags=None, auto_quote=True, auto_tags=True):
    """Обёртка для обратной совместимости"""
    if file_path and os.path.exists(file_path):
        return publish_content(bot, chat_id, file_path, caption=message, auto_quote=auto_quote, auto_tags=auto_tags)
    elif message:
        return publish_content(bot, chat_id, message, auto_quote=auto_quote, auto_tags=auto_tags)
    return False
