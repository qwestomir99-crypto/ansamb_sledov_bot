# ==========================================
# Файл: services/autoposter.py
# Справка: README.md → Автопостинг YouTube
# Задача: публикация случайного видео из плейлиста в VK с превью
# Комментарий: видео отправляется как attachment, чтобы VK показывал обложку.
#              Использует dialogue.youtube_auto для получения видео.
#              Исправлена обработка отсутствия медиа — публикует только текст,
#              если видео не прикрепляется.
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

def post_to_vk_with_preview(message, video_url, access_token, owner_id):
    """
    Отправляет пост в VK с видео-ссылкой как attachment.
    Это заставляет VK показывать превью (обложку видео).
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
    
    full_message = f"{message}\n\n{default_tags}"
    
    params = {
        "access_token": access_token,
        "v": "5.199",
        "owner_id": owner_id,
        "message": full_message,
        "from_group": 1
    }
    
    # Пытаемся прикрепить видео
    if video_url:
        params["attachments"] = video_url
    else:
        log_auto("WARNING", "Видео не прикрепляется, публикуем только текст")
    
    try:
        r = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
        data = r.json()
        
        if "response" in data:
            log_auto("INFO", f"✅ Опубликовано в VK: {message[:50]}...")
            return True, None
        else:
            error_msg = data.get("error", {}).get("error_msg", "неизвестная ошибка")
            # Если ошибка связана с видео, пробуем без attachments
            if "link_photo_sizing_rule" in error_msg or "No photo given" in error_msg:
                log_auto("WARNING", f"Ошибка с видео: {error_msg}. Пробуем без attachments.")
                del params["attachments"]
                try:
                    r2 = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
                    data2 = r2.json()
                    if "response" in data2:
                        log_auto("INFO", f"✅ Опубликовано без видео: {message[:50]}...")
                        return True, None
                    else:
                        error_msg2 = data2.get("error", {}).get("error_msg", "неизвестная ошибка")
                        log_auto("ERROR", f"Ошибка VK (без видео): {error_msg2}")
                        return False, error_msg2
                except Exception as e2:
                    log_auto("ERROR", f"Исключение при повторной попытке: {e2}")
                    return False, str(e2)
            else:
                log_auto("ERROR", f"Ошибка VK: {error_msg}")
                return False, error_msg
    except Exception as e:
        log_auto("ERROR", f"Исключение VK: {e}")
        return False, str(e)

# ==========================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==========================================
def check_and_publish():
    """Публикует случайное видео из плейлиста в VK с превью"""
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
    
    success, error = post_to_vk_with_preview(post_text, video['url'], vk_token, vk_owner_id)
    
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
