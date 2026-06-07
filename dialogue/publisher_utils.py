# ==========================================
# Файл: dialogue/publisher_utils.py
# Справка: README.md → Публикатор / Утилиты
# Задача: отправка постов в Telegram и VK
# Комментарий: VK — старый метод wall.post + авто-рефреш
# ==========================================

import os, random, json, requests
from utils import escape_markdown
from debug_utils import debug_log

CONFIG_FILE = "config.json"
QUOTES_FILE = "dialogue/data/quotes.txt"

def load_config():
    with open(CONFIG_FILE, "r") as f: return json.load(f)

def load_quotes():
    if not os.path.exists(QUOTES_FILE): return []
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_random_quote():
    quotes = load_quotes()
    return random.choice(quotes) if quotes else "Ритм 0,8 Гц стабилен. Сеть тлеет."

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

def get_vk_upload_url(vk_token, owner_id):
    try:
        r = requests.get("https://api.vk.com/method/photos.getWallUploadServer", params={"access_token": vk_token, "v": "5.199", "owner_id": owner_id}, timeout=10)
        return r.json().get("response", {}).get("upload_url")
    except: return None

def upload_photo_to_vk(upload_url, file_data, vk_token):
    try:
        files = {'photo': ('photo.jpg', file_data)}
        r = requests.post(upload_url, files=files)
        data = r.json()
        save_params = {"access_token": vk_token, "v": "5.199", "photo": data['photo'], "server": data['server'], "hash": data['hash']}
        r = requests.get("https://api.vk.com/method/photos.saveWallPhoto", params=save_params)
        photo_data = r.json()
        if 'response' in photo_data and photo_data['response']:
            photo = photo_data['response'][0]
            return f"photo{photo['owner_id']}_{photo['id']}"
    except: return None

def post_to_telegram(bot, chat_id, message, file_id=None, tags=None, auto_quote=True, auto_tags=True):
    if auto_quote and message and len(message) < 500:
        message = f"{message}\n\n📜 {get_random_quote()}"
    if auto_tags: tags = get_auto_tags(message, "tg")
    full_message = f"{message}\n\n{tags}" if tags and message else (tags or message)
    safe = escape_markdown(full_message) if full_message else None
    try:
        if file_id:
            import telebot
            bot2 = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
            file_info = bot2.get_file(file_id)
            downloaded = bot2.download_file(file_info.file_path)
            ext = os.path.splitext(file_info.file_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                bot.send_photo(chat_id, downloaded, caption=safe, parse_mode='MarkdownV2')
            elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
                bot.send_video(chat_id, downloaded, caption=safe, parse_mode='MarkdownV2')
            else:
                bot.send_document(chat_id, downloaded, caption=safe, parse_mode='MarkdownV2')
            return True
        elif safe:
            bot.send_message(chat_id, safe, parse_mode='MarkdownV2')
            return True
        return False
    except Exception as e:
        debug_log("PUBLISHER", f"Ошибка TG: {e}", "ERROR")
        return False

def get_vk_token():
    token = os.environ.get("VK_TOKEN_USER")
    if token and len(token) > 80: return token
    token = os.environ.get("VK_TOKEN")
    if token: return token
    try:
        from services.app import refresh_vk_token
        token = refresh_vk_token()
        if token: return token
    except: pass
    return None

def post_to_vk(message, tags, access_token, owner_id, file_id=None, auto_quote=True, auto_tags=True, repost_from=None):
    if not access_token: access_token = get_vk_token()
    if not access_token or not owner_id:
        debug_log("VK", "Нет токена или owner_id", "ERROR")
        return False, "Ошибка авторизации VK"
    
    if auto_quote and message and len(message) < 500:
        message = f"{message}\n\n📜 {get_random_quote()}"
    if auto_tags: tags = get_auto_tags(message, "vk")
    full_message = f"{message}\n\n{tags}" if tags else message
    
    # Пробуем разные комбинации параметров
    for owner_format in [int(owner_id), -int(owner_id)]:
        for from_grp in [0, 1, None]:
            params = {"access_token": access_token, "v": "5.199", "owner_id": owner_format, "message": full_message}
            if from_grp is not None: params["from_group"] = from_grp
            
            try:
                r = requests.get('https://api.vk.com/method/wall.post', params=params, timeout=30)
                data = r.json()
                if 'response' in data:
                    debug_log("VK", f"Опубликовано! owner_id={owner_format}, from_group={from_grp}")
                    return True, None
                else:
                    error_msg = data.get('error', {}).get('error_msg', '')
                    if 'profile type' not in error_msg.lower():
                        debug_log("VK", f"Ошибка ({owner_format}, {from_grp}): {error_msg}", "WARNING")
            except: pass
    
    debug_log("VK", "Все варианты перебраны, публикация не удалась", "ERROR")
    return False, "VK: все попытки не удались"
