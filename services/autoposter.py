# ==========================================
# Файл: services/autoposter.py
# Справка: README.md → Автопостинг YouTube
# Задача: публикация случайного видео из плейлиста в TG и VK
# Комментарий: TG — всегда, VK — ждёт пользовательский токен
# ==========================================

import os
import random
import json
import time
import requests
from debug_utils import debug_log
from dialogue.youtube_auto import get_random_video

def log_auto(level, message):
    debug_log("AUTOPOSTER", message, level)

def get_random_quote():
    quotes_file = "dialogue/data/quotes.txt"
    if not os.path.exists(quotes_file):
        return "Ритм 0,8 Гц стабилен. Сеть тлеет."
    try:
        with open(quotes_file, "r", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
        return random.choice(quotes) if quotes else "Сеть тлеет. Ритм 0,8 Гц."
    except:
        return "Сеть тлеет. Ритм 0,8 Гц."

def post_to_tg(bot, tg_chat_id, message, video_url):
    """Публикует видео в Telegram-канал"""
    quote = get_random_quote()
    full_text = f"📜 {quote}\n\n🎬 {message}\n{video_url}"
    try:
        bot.send_message(tg_chat_id, full_text)
        log_auto("INFO", f"Видео опубликовано в TG: {message[:50]}...")
        return True
    except Exception as e:
        log_auto("ERROR", f"Ошибка TG: {e}")
        return False

def post_to_vk_profile(message, video_url, access_token, owner_id):
    """Пост в личный профиль VK (если токен рабочий)"""
    if not access_token or not owner_id or len(access_token) <= 80:
        log_auto("WARNING", "VK отключён (нужен пользовательский токен)")
        return False, "VK отключён"
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        default_tags = config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
    except:
        default_tags = "#Ансамбль #СледНаКонтаке"
    
    full_message = f"{message}\n\n📌 {video_url}\n\n{default_tags}"
    
    params = {
        "access_token": access_token,
        "v": "5.199",
        "owner_id": int(owner_id),
        "message": full_message
    }
    
    try:
        r = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
        data = r.json()
        if "response" in data:
            log_auto("INFO", f"Видео опубликовано в VK: {message[:50]}...")
            return True, None
        else:
            error_msg = data.get("error", {}).get("error_msg", "неизвестная ошибка")
            log_auto("ERROR", f"Ошибка VK: {error_msg}")
            return False, error_msg
    except Exception as e:
        log_auto("ERROR", f"Исключение VK: {e}")
        return False, str(e)

def check_and_publish(bot, tg_chat_id):
    """Проверяет видео и публикует в TG (и VK если можно)"""
    log_auto("INFO", "Проверка видео из плейлиста...")
    
    video = get_random_video()
    if not video:
        log_auto("WARNING", "Не удалось получить видео из плейлиста")
        return
    
    log_auto("INFO", f"Получено видео: {video['title'][:50]}...")
    
    # TG — всегда
    post_to_tg(bot, tg_chat_id, video['title'], video['url'])
    
    # VK — если есть токен
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    if vk_token and vk_owner_id:
        post_to_vk_profile(video['title'], video['url'], vk_token, vk_owner_id)

def start_autoposter(config=None, vk_token=None, vk_owner_id=None):
    log_auto("INFO", "Автопостинг YouTube запущен (TG + VK, раз в день)")
    import bot
    # Получаем бота и канал
    from bot.core import get_bot
    bot_instance = get_bot()
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir") if config else "@qwestomir"
    
    while True:
        try:
            check_and_publish(bot_instance, tg_chat_id)
        except Exception as e:
            log_auto("ERROR", f"Ошибка в цикле: {e}")
        time.sleep(86400)
