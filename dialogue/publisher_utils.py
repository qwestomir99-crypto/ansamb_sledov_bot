# ==========================================
# Файл: dialogue/publisher_utils.py
# Справка: README.md → Публикатор / Утилиты
# Задача: отправка постов в Telegram и VK с авто-обновлением токена
# Комментарий: VK — группа от имени пользователя
# ==========================================

import os, random, json, requests
from utils import escape_markdown
from debug_utils import debug_log

CONFIG_FILE = "config.json"
QUOTES_FILE = "dialogue/data/quotes.txt"
VK_POSTS_FILE = "dialogue/data/vk_posts.json"

def load_config():
    with open(CONFIG_FILE, "r") as f: return json.load(f)

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

def get_auto_tags(text, platform="vk"):
    config = load_config()
    tags = set()
    if platform == "vk":
        tags.update(config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке").split())
    else:
        tags.update(config.get("publisher", {}).get("default_tags", "#СапёрыАутентичности #МихоельАв #2026плита").split())
    for w in text.split():
        if w.startswith('#'): tags.add(w)
    return " ".join(tags)

def get_vk_token():
    token = os.environ.get("VK_TOKEN_USER")
    if not token:
        try:
            from services.app import refresh_vk_token
            token = refresh_vk_token()
        except: pass
    return token

def post_to_vk(message, tags, access_token, owner_id, file_paths=None, auto_quote=True, auto_tags=True, repost_from=None):
    if not access_token: access_token = get_vk_token()
    if not access_token or not owner_id: return False, "Ошибка авторизации VK"
    
    if auto_quote and message and len(message) < 500:
        message = f"{message}\n\n📜 {get_random_quote()}"
    if auto_tags: tags = get_auto_tags(message, "vk")
    full_message = f"{message}\n\n{tags}" if message else tags
    
    params = {"access_token": access_token, "v": "5.199", "owner_id": -int(owner_id), "message": full_message, "from_group": 0}
    
    try:
        r = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=30)
        data = r.json()
        if 'response' in data:
            debug_log("VK", "Опубликовано в VK")
            return True, None
        else:
            error_msg = data.get('error', {}).get('error_msg', 'неизвестная')
            if 'expired' in error_msg.lower():
                try:
                    from services.app import refresh_vk_token
                    new_token = refresh_vk_token()
                    if new_token:
                        params["access_token"] = new_token
                        r2 = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=30)
                        d2 = r2.json()
                        if 'response' in d2:
                            debug_log("VK", "Опубликовано в VK (после рефреша)")
                            return True, None
                except: pass
            debug_log("VK", f"Ошибка: {error_msg}", "ERROR")
            return False, f"Ошибка VK: {error_msg}"
    except Exception as e:
        debug_log("VK", f"Исключение: {e}", "ERROR")
        return False, f"Ошибка сети: {e}"
