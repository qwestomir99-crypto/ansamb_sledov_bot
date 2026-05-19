# ==========================================
# Модуль: services/autoposter.py
# Задача: автоматическая проверка YouTube и публикация новых видео в VK
# Работает через scheduler.py и activity_modes.py
# ==========================================

import os
import time
import json
import requests
from datetime import datetime

# Файл для хранения ID последнего опубликованного видео
LAST_VIDEO_FILE = "dialogue/data/last_youtube_video.txt"

def log(msg, level="INFO"):
    print(f"[AUTOPOSTER] {level}: {msg}")

def get_last_published_video():
    """Возвращает ID последнего опубликованного видео"""
    if os.path.exists(LAST_VIDEO_FILE):
        with open(LAST_VIDEO_FILE, "r") as f:
            return f.read().strip()
    return None

def save_last_published_video(video_id):
    """Сохраняет ID последнего опубликованного видео"""
    os.makedirs(os.path.dirname(LAST_VIDEO_FILE), exist_ok=True)
    with open(LAST_VIDEO_FILE, "w") as f:
        f.write(video_id)

def get_latest_video_from_channel():
    """Получает последнее видео с канала через YouTube API"""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    channel_id = os.environ.get("YOUTUBE_CHANNEL_ID")
    
    if not api_key:
        log("YOUTUBE_API_KEY не настроен", "ERROR")
        return None
    
    if not channel_id:
        log("YOUTUBE_CHANNEL_ID не настроен", "ERROR")
        return None
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "maxResults": 1,
        "order": "date",
        "type": "video",
        "key": api_key
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        
        if "error" in data:
            log(f"API ошибка: {data['error']['message']}", "ERROR")
            return None
        
        if "items" in data and data["items"]:
            item = data["items"][0]
            return {
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"]
            }
        
        log("Видео не найдены", "WARNING")
        return None
    except Exception as e:
        log(f"Ошибка запроса: {e}", "ERROR")
        return None

def get_random_quote():
    """Берёт случайную цитату из файла"""
    quotes_file = "dialogue/data/quotes.txt"
    if not os.path.exists(quotes_file):
        return "Ритм 0,8 Гц стабилен. Сеть тлеет."
    
    with open(quotes_file, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    
    import random
    return random.choice(quotes) if quotes else "Сеть тлеет. Ритм 0,8 Гц."

def post_to_vk(message, access_token, owner_id):
    """Отправляет пост в VK"""
    if not access_token or not owner_id:
        log("Нет токена VK или owner_id", "ERROR")
        return False, "Нет авторизации VK"
    
    # Добавляем хештеги из конфига
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
    
    try:
        r = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
        data = r.json()
        
        if "response" in data:
            log(f"✅ Опубликовано в VK: {message[:50]}...")
            return True, None
        else:
            error_msg = data.get("error", {}).get("error_msg", "неизвестная ошибка")
            log(f"Ошибка VK: {error_msg}", "ERROR")
            return False, error_msg
    except Exception as e:
        log(f"Исключение VK: {e}", "ERROR")
        return False, str(e)

def check_and_publish():
    """
    Проверяет новые видео и публикует их.
    Эту функцию будет вызывать scheduler по расписанию.
    """
    log("Проверка новых видео на YouTube...")
    
    latest = get_latest_video_from_channel()
    if not latest:
        log("Не удалось получить видео с канала", "WARNING")
        return False
    
    last_published = get_last_published_video()
    
    if last_published == latest["id"]:
        log(f"Новых видео нет. Последнее: {latest['id']}")
        return False
    
    # Новое видео найдено!
    log(f"🔥 НОВОЕ ВИДЕО: {latest['title']} (ID: {latest['id']})")
    
    # Берём случайную цитату
    quote = get_random_quote()
    
    # Формируем пост
    video_url = f"https://youtu.be/{latest['id']}"
    post_text = f"📜 *{quote}*\n\n🎬 *НОВОЕ ВИДЕО НА КАНАЛЕ*\n{latest['title']}\n\n{video_url}"
    
    # Публикуем в VK
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    success, error = post_to_vk(post_text, vk_token, vk_owner_id)
    
    if success:
        save_last_published_video(latest["id"])
        log("✅ Видео успешно опубликовано в VK!")
        return True
    else:
        log(f"❌ Ошибка публикации: {error}", "ERROR")
        return False

def start_autoposter(config=None, vk_token=None, vk_owner_id=None):
    """
    Заглушка для обратной совместимости.
    Реальное расписание управляется через scheduler.py.
    """
    log("Автопостинг YouTube настроен. Расписание управляется через scheduler.py")
    log("Проверка будет выполняться согласно activity_modes.py")
    
    # Для тестирования можно сделать один вызов
    if config and config.get("autoposter", {}).get("test_on_start", False):
        check_and_publish()

# Для самостоятельного тестирования
if __name__ == "__main__":
    print("Тестирование автопостинга...")
    check_and_publish()
