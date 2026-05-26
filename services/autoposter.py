# ==========================================
# Файл: services/autoposter.py
# Справка: README.md → Автопостинг YouTube
# Задача: публикация случайного видео из плейлиста в VK
# Комментарий: если не удаётся прикрепить видео как attachment (превью),
#              публикуем текст с прямой ссылкой на видео — так пост не пустой.
#              Использует dialogue.youtube_auto для получения видео.
# Зависит от: requests, os, random, json, debug_utils, dialogue.youtube_auto
# Вызывается из: bot.py (отдельный поток)
# ==========================================

import os
import random
import json
import requests
from debug_utils import debug_log

# Импортируем модуль для работы с плейлистом
from dialogue.youtube_auto import get_random_video

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def log_auto(level, message):
    debug_log("AUTOPOSTER", message, level)

def get_random_quote():
    """Берёт случайную цитату из файла"""
    quotes_file = "dialogue/data/quotes.txt"
    if not os.path.exists(quotes_file):
        log_auto("WARNING", "Файл цитат не найден")
        return "Ритм 0,8 Гц стабилен. Сеть тлеет."
    
    try:
        with open(quotes_file, "r", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
        
        quote = random.choice(quotes) if quotes else "Сеть тлеет. Ритм 0,8 Гц."
        log_auto("INFO", f"📜 Выбрана цитата: {quote[:50]}...")
        return quote
    except Exception as e:
        log_auto("ERROR", f"Ошибка чтения цитат: {e}")
        return "Сеть тлеет. Ритм 0,8 Гц."

def post_to_vk_with_link(message, video_url, access_token, owner_id):
    """
    Отправляет пост в VK, где видео — обычная ссылка в тексте,
    а не attachment. Так пост не будет пустым, даже если превью не подтягивается.
    """
    if not access_token or not owner_id:
        log_auto("ERROR", "Нет токена VK или owner_id")
        return False, "Нет авторизации VK"
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        default_tags = config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
    except:
        default_tags = "#Ансамбль #СледНаКонтаке"
    
    full_message = f"{message}\n\n📌 Ссылка на видео: {video_url}\n\n{default_tags}"
    
    params = {
        "access_token": access_token,
        "v": "5.199",
        "owner_id": owner_id,
        "message": full_message,
        "from_group": 1
    }
    
    try:
        r = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
        data = r.json()
        
        if "response" in data:
            log_auto("INFO", f"✅ Опубликовано в VK со ссылкой: {message[:50]}...")
            return True, None
        else:
            error_msg = data.get("error", {}).get("error_msg", "неизвестная ошибка")
            log_auto("ERROR", f"Ошибка VK: {error_msg}")
            return False, error_msg
    except Exception as e:
        log_auto("ERROR", f"Исключение VK: {e}")
        return False, str(e)

# ==========================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==========================================
def check_and_publish():
    """Публикует случайное видео из плейлиста в VK со ссылкой"""
    log_auto("INFO", "=" * 50)
    log_auto("INFO", "НАЧАЛО ПУБЛИКАЦИИ СЛУЧАЙНОГО ВИДЕО ИЗ ПЛЕЙЛИСТА")
    log_auto("INFO", "=" * 50)
    
    try:
        from dialogue.adaptive_modes import should_adaptive_publish
        if not should_adaptive_publish():
            log_auto("INFO", "Режим тишины (аврал/сон) — публикация отложена")
            return False
    except ImportError:
        log_auto("WARNING", "adaptive_modes не найден, продолжаем без проверки")
    
    # Используем модуль youtube_auto для получения случайного видео из плейлиста
    video = get_random_video()
    if not video:
        log_auto("WARNING", "Не удалось получить видео из плейлиста")
        return False
    
    quote = get_random_quote()
    
    post_text = f"📜 *{quote}*\n\n🎬 *СЛУЧАЙНОЕ ВИДЕО ИЗ ПЛЕЙЛИСТА*\n{video['title']}"
    
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    success, error = post_to_vk_with_link(post_text, video['url'], vk_token, vk_owner_id)
    
    if success:
        log_auto("INFO", "✅ Случайное видео из плейлиста успешно опубликовано в VK!")
        return True
    else:
        log_auto("ERROR", f"❌ Ошибка публикации: {error}")
        return False

def start_autoposter(config=None, vk_token=None, vk_owner_id=None):
    """Заглушка для обратной совместимости"""
    log_auto("INFO", "Автопостинг YouTube (случайные видео из плейлиста) настроен.")
    
    if config and config.get("autoposter", {}).get("test_on_start", False):
        check_and_publish()

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ АВТОПОСТЕРА ===")
    check_and_publish()
