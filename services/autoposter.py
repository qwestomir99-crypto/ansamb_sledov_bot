# ==========================================
# Файл: services/autoposter.py
# Справка: README.md → Автопостинг YouTube
# Задача: публикация случайных видео с YouTube в VK с превью
# Комментарий: видео отправляется как attachment, чтобы VK показывал обложку
# Зависит от: requests, os, random, json
# Вызывается из: bot.py (отдельный поток)
# ==========================================

import os
import random
import json
import requests

def log(msg, level="INFO"):
    print(f"[AUTOPOSTER] {level}: {msg}")

def get_random_video_from_channel():
    """Получает случайное видео с канала через YouTube API"""
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
        "maxResults": 50,
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
        
        items = data.get("items", [])
        if not items:
            log("Видео не найдены", "WARNING")
            return None
        
        item = random.choice(items)
        
        video = {
            "id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"],
            "url": f"https://youtu.be/{item['id']['videoId']}"
        }
        log(f"🎲 Выбрано случайное видео: {video['title']} (ID: {video['id']})")
        return video
        
    except Exception as e:
        log(f"Ошибка запроса: {e}", "ERROR")
        return None

def get_random_quote():
    """Берёт случайную цитату из файла"""
    quotes_file = "dialogue/data/quotes.txt"
    if not os.path.exists(quotes_file):
        log("Файл цитат не найден", "WARNING")
        return "Ритм 0,8 Гц стабилен. Сеть тлеет."
    
    with open(quotes_file, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    
    quote = random.choice(quotes) if quotes else "Сеть тлеет. Ритм 0,8 Гц."
    log(f"📜 Выбрана цитата: {quote[:50]}...")
    return quote

def post_to_vk_with_preview(message, video_url, access_token, owner_id):
    """
    Отправляет пост в VK с видео-ссылкой как attachment.
    Это заставляет VK показывать превью (обложку видео).
    """
    if not access_token or not owner_id:
        log("Нет токена VK или owner_id", "ERROR")
        return False, "Нет авторизации VK"
    
    # Добавляем хештеги
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        default_tags = config.get("autoposter", {}).get("vk_tags", "#Ансамбль #СледНаКонтаке")
    except:
        default_tags = "#Ансамбль #СледНаКонтаке"
    
    full_message = f"{message}\n\n{default_tags}"
    
    # Отправляем ссылку как attachment — VK подтянет превью
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
            log(f"✅ Опубликовано в VK с превью: {message[:50]}...")
            return True, None
        else:
            error_msg = data.get("error", {}).get("error_msg", "неизвестная ошибка")
            log(f"Ошибка VK: {error_msg}", "ERROR")
            return False, error_msg
    except Exception as e:
        log(f"Исключение VK: {e}", "ERROR")
        return False, str(e)

def check_and_publish():
    """Публикует случайное видео с YouTube в VK с превью"""
    log("=== НАЧАЛО ПУБЛИКАЦИИ СЛУЧАЙНОГО ВИДЕО ===")
    
    try:
        from dialogue.adaptive_modes import should_adaptive_publish
        if not should_adaptive_publish():
            log("Режим тишины (аврал/сон) — публикация отложена")
            return False
    except ImportError:
        log("adaptive_modes не найден, продолжаем без проверки")
    
    video = get_random_video_from_channel()
    if not video:
        log("Не удалось получить видео с канала", "WARNING")
        return False
    
    quote = get_random_quote()
    
    post_text = f"📜 *{quote}*\n\n🎬 *СЛУЧАЙНОЕ ВИДЕО С КАНАЛА*\n{video['title']}"
    
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    # Отправляем с video_url как attachment для превью
    success, error = post_to_vk_with_preview(post_text, video['url'], vk_token, vk_owner_id)
    
    if success:
        log("✅ Случайное видео успешно опубликовано в VK с превью!")
        return True
    else:
        log(f"❌ Ошибка публикации: {error}", "ERROR")
        return False

def start_autoposter(config=None, vk_token=None, vk_owner_id=None):
    """Заглушка для обратной совместимости"""
    log("Автопостинг YouTube (случайные видео) настроен. Проверка выполняется отдельным потоком.")
    
    if config and config.get("autoposter", {}).get("test_on_start", False):
        check_and_publish()

if __name__ == "__main__":
    print("Тестирование автопостинга...")
    check_and_publish()
