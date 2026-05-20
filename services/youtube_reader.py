# ==========================================
# Файл: services/youtube_reader.py
# Справка: README.md → YouTube Reader
# Задача: чтение видео с YouTube канала (без публикации)
# Комментарий: используется для тестов и диагностики YouTube API
# Зависит от: requests, os
# Вызывается из: handlers.py (команда #ютуб_тест)
# ==========================================

import os
import requests

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID")

def log(msg, level="INFO"):
    print(f"[YOUTUBE] {level}: {msg}")

def get_channel_videos(max_results=3):
    """Получает последние видео с канала через YouTube API"""
    if not YOUTUBE_API_KEY:
        log("API ключ не настроен (YOUTUBE_API_KEY отсутствует)", "WARNING")
        return []
    
    if not YOUTUBE_CHANNEL_ID:
        log("ID канала не настроен (YOUTUBE_CHANNEL_ID отсутствует)", "WARNING")
        return []
    
    log(f"Запрос видео с канала {YOUTUBE_CHANNEL_ID}")
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": YOUTUBE_CHANNEL_ID,
        "maxResults": max_results,
        "order": "date",
        "type": "video",
        "key": YOUTUBE_API_KEY
    }
    
    try:
        r = requests.get(url, params=params, timeout=10)
        
        if r.status_code != 200:
            log(f"HTTP ошибка: {r.status_code}", "ERROR")
            return []
        
        data = r.json()
        
        if "error" in data:
            log(f"API ошибка: {data['error']['message']}", "ERROR")
            return []
        
        videos = []
        for item in data.get("items", []):
            videos.append({
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "published_at": item["snippet"]["publishedAt"]
            })
        
        log(f"Получено {len(videos)} видео")
        return videos
    except Exception as e:
        log(f"Ошибка запроса: {type(e).__name__} - {e}", "ERROR")
        return []

def get_last_video():
    """Возвращает последнее видео с канала"""
    log("Поиск последнего видео...")
    videos = get_channel_videos(1)
    if not videos:
        log("Видео не найдены", "WARNING")
        return None
    log(f"Последнее видео: {videos[0]['title']}")
    return videos[0]

def test_youtube():
    """Тестовая функция для проверки подключения к YouTube API"""
    log("=== ТЕСТ ПОДКЛЮЧЕНИЯ К YOUTUBE ===")
    
    if not YOUTUBE_API_KEY:
        log("❌ YOUTUBE_API_KEY не задан", "ERROR")
        return False
    
    if not YOUTUBE_CHANNEL_ID:
        log("❌ YOUTUBE_CHANNEL_ID не задан", "ERROR")
        return False
    
    log(f"✅ API ключ: {YOUTUBE_API_KEY[:10]}...")
    log(f"✅ ID канала: {YOUTUBE_CHANNEL_ID}")
    
    video = get_last_video()
    if video:
        log(f"✅ Найдено видео: {video['title']}")
        return True
    else:
        log("❌ Не удалось получить видео", "ERROR")
        return False

if __name__ == "__main__":
    test_youtube()
