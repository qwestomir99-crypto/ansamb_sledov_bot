# ==========================================
# Файл: services/autoposter.py
# Справка: README.md → Автопостинг YouTube
# Задача: публикация случайного видео из плейлиста в VK (личный профиль)
# Комментарий: запуск раз в день (86400 сек), логи через debug_utils
# Зависит от: requests, os, random, json, time, debug_utils, dialogue.youtube_auto
# Вызывается из: bot.py (отдельный поток)
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

def post_to_vk_profile(message, video_url, access_token, owner_id):
    if not access_token or not owner_id:
        log_auto("ERROR", "Нет токена VK или owner_id")
        return False, "Нет авторизации VK"
    
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

def check_and_publish():
    log_auto("INFO", "Проверка видео из плейлиста...")
    
    video = get_random_video()
    if not video:
        log_auto("WARNING", "Не удалось получить видео из плейлиста")
        return False
    
    log_auto("INFO", f"Получено видео: {video['title'][:50]}...")
    
    quote = get_random_quote()
    post_text = f"📜 {quote}\n\n🎬 {video['title']}"
    
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    if not vk_token or not vk_owner_id:
        log_auto("ERROR", "VK_TOKEN или VK_OWNER_ID не заданы")
        return False
    
    log_auto("INFO", "Публикация в VK (профиль)...")
    success, error = post_to_vk_profile(post_text, video['url'], vk_token, vk_owner_id)
    
    if success:
        log_auto("INFO", "Видео из плейлиста опубликовано в VK")
    else:
        log_auto("ERROR", f"Ошибка публикации: {error}")
    
    return success

def start_autoposter(config=None, vk_token=None, vk_owner_id=None):
    log_auto("INFO", "Автопостинг YouTube запущен (личный профиль, раз в день)")
    while True:
        try:
            check_and_publish()
        except Exception as e:
            log_auto("ERROR", f"Ошибка в цикле: {e}")
        time.sleep(86400)
