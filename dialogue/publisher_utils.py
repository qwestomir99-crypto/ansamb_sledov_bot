# ==========================================
# Файл: dialogue/publisher_utils.py
# Справка: README.md → Публикатор / Утилиты
# Задача: отправка постов в Telegram и VK
# Комментарий: VK использует VK_TOKEN_USER
# ==========================================

import os
import random
import json
import requests
from utils import escape_markdown
from debug_utils import debug_log

CONFIG_FILE = "config.json"
QUOTES_FILE = "dialogue/data/quotes.txt"
VK_POSTS_FILE = "dialogue/data/vk_posts.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_quotes():
    if not os.path.exists(QUOTES_FILE): return []
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_random_quote():
    quotes = load_quotes()
    return random.choice(quotes) if quotes else "Ритм 0,8 Гц стабилен. Сеть тлеет."

def load_vk_posts():
    if not os.path.exists(VK_POSTS_FILE): return []
    try:
        with open(VK_POSTS_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data: return []
            return json.loads(data)
    except: return []

def get_random_own_post_from_vk():
    posts = load_vk_posts()
    if not posts: return None
    posts_with_media = [p for p in posts if p.get("attachments") or p.get("text")]
    if not posts_with_media: posts_with_media = posts
    post = random.choice(posts_with_media)
    return {"post_id": post.get("id"), "text": post.get("text", ""), "attachments": post.get("attachments", []), "date": post.get("date")}

def get_auto_tags(text, platform="vk"):
    config = load_config()
    tags = set()
    if platform == "vk":
        vk_tags = config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
        tags.update(vk_tags.split())
    else:
        default_tags = config.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита")
        tags.update(default_tags.split())
    for w in text.split():
        if w.startswith('#'): tags.add(w)
    return " ".join(tags)

def post_to_vk(message, tags, access_token, owner_id, file_paths=None, auto_quote=True, auto_tags=True, repost_from=None):
    debug_log("VK", f"post_to_vk: message={message[:50] if message else ''}...")
    if not access_token or not owner_id: return False, "Ошибка авторизации VK"
    if auto_quote and message and len(message) < 500: message = f"{message}\n\n📜 {get_random_quote()}"
    if auto_tags: tags = get_auto_tags(message, "vk")
    full_message = f"{message}\n\n{tags}" if message else tags
    
    params = {"access_token": access_token, "v": "5.199", "owner_id": int(owner_id), "message": full_message}
    try:
        r = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=30)
        data = r.json()
        if 'response' in data:
            debug_log("VK", "Опубликовано в VK")
            return True, None
        else:
            error_msg = data.get('error', {}).get('error_msg', 'неизвестная')
            debug_log("VK", f"Ошибка: {error_msg}", "ERROR")
            return False, f"Ошибка VK: {error_msg}"
    except Exception as e:
        debug_log("VK", f"Исключение: {e}", "ERROR")
        return False, f"Ошибка сети: {e}"
