# ==========================================
# Файл: services/autoposter.py
# Справка: README.md → Автопостинг YouTube
# Задача: публикация случайного видео из плейлиста в VK с превью
# Комментарий: видео отправляется как attachment, чтобы VK показывал обложку.
#              Использует dialogue.youtube_auto для получения видео.
# Зависит от: requests, os, random, json
# Вызывается из: bot.py (отдельный поток)
# ==========================================

import os
import random
import json
import requests
from debug_utils import debug_log

# Импортируем модуль для работы с плейлистом
from dialogue.youtube_auto import get_random_video

def get_random_quote():
    """Берёт случайную цитату из файла"""
    quotes_file = "dialogue/data/quotes.txt"
    if not os.path.exists(quotes_file):
        debug_log("AUTOPOSTER", "Файл цитат не найден", "WARNING")
        return "Ритм 0,8 Гц стабилен. Сеть тлеет."
    
    with open(quotes_file, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    
    quote = random.choice(quotes) if quotes else "Сеть тлеет. Ритм 0,8 Гц."
    debug_log("AUTOPOSTER", f"📜 Выбрана цитата: {quote[:50]}...")
    return quote

def post_to_vk_with_preview(message, video_url, access_token, owner_id):
    """
    Отправляет пост в VK с видео-ссылкой как attachment.
    Это заставляет VK показывать превью (обложку видео).
    """
    if not access_token or not owner_id:
        debug_log("AUTOPOSTER", "Нет токена VK или owner_id", "ERROR")
        return False, "Нет авторизации VK"
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        default_tags = config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
    except:
        default_tags = "#Ансамбль #СледНаКонтаке"
    
    full_message = f"{message}\n\n{default_tags}"
    
    params = {
        "access_token": access_token,
        "v": "5.199",
        "owner_id": owner_id,
        "message": full_message,
        "attachments": video_url,
        "from_group": 1
    }
    
    try:
        r = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
        data = r.json()
        
        if "response" in data:
            debug_log("AUTOPOSTER", f"✅ Опубликовано в VK с превью: {message[:50]}...")
            return True, None
        else:
            error_msg = data.get("error", {}).get("error_msg", "неизвестная ошибка")
            debug_log("AUTOPOSTER", f"Ошибка VK: {error_msg}", "ERROR")
            return False, error_msg
    except Exception as e:
        debug_log("AUTOPOSTER", f"Исключение VK: {e}", "ERROR")
        return False, str(e)

def check_and_publish():
    """Публикует случайное видео из плейлиста в VK с превью"""
    debug_log("AUTOPOSTER", "=== НАЧАЛО ПУБЛИКАЦИИ СЛУЧАЙНОГО ВИДЕО ИЗ ПЛЕЙЛИСТА ===")
    
    try:
        from dialogue.adaptive_modes import should_adaptive_publish
        if not should_adaptive_publish():
            debug_log("AUTOPOSTER", "Режим тишины (аврал/сон) — публикация отложена")
            return False
    except ImportError:
        debug_log("AUTOPOSTER", "adaptive_modes не найден, продолжаем без проверки", "WARNING")
    
    # Используем модуль youtube_auto для получения случайного видео из плейлиста
    video = get_random_video()
    if not video:
        debug_log("AUTOPOSTER", "Не удалось получить видео из плейлиста", "WARNING")
        return False
    
    quote = get_random_quote()
    
    post_text = f"📜 *{quote}*\n\n🎬 *СЛУЧАЙНОЕ ВИДЕО ИЗ ПЛЕЙЛИСТА*\n{video['title']}"
    
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    success, error = post_to_vk_with_preview(post_text, video['url'], vk_token, vk_owner_id)
    
    if success:
        debug_log("AUTOPOSTER", "✅ Случайное видео из плейлиста успешно опубликовано в VK с превью!")
        return True
    else:
        debug_log("AUTOPOSTER", f"❌ Ошибка публикации: {error}", "ERROR")
        return False

def start_autoposter(config=None, vk_token=None, vk_owner_id=None):
    """Заглушка для обратной совместимости"""
    debug_log("AUTOPOSTER", "Автопостинг YouTube (случайные видео из плейлиста) настроен. Проверка выполняется отдельным потоком.")
    
    if config and config.get("autoposter", {}).get("test_on_start", False):
        check_and_publish()

if __name__ == "__main__":
    check_and_publish()
