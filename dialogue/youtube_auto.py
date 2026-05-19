# ==========================================
# Модуль: dialogue/youtube_auto.py
# Задача: работа с YouTube API (получение видео, проверка новых)
# ==========================================

import os
import requests
import json

def log(msg, level="INFO"):
    print(f"[YOUTUBE_AUTO] {level}: {msg}")

def get_youtube_api_key():
    """Получает API ключ из переменных окружения"""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        log("YOUTUBE_API_KEY не задан", "ERROR")
    return api_key

def get_youtube_channel_id():
    """Получает ID канала из переменных окружения"""
    channel_id = os.environ.get("YOUTUBE_CHANNEL_ID")
    if not channel_id:
        log("YOUTUBE_CHANNEL_ID не задан", "ERROR")
    return channel_id

def get_latest_video(channel_id=None, api_key=None, max_results=1):
    """
    Получает последние видео с канала.
    
    Args:
        channel_id: ID канала YouTube
        api_key: API ключ YouTube
        max_results: количество видео (по умолчанию 1)
    
    Returns:
        list: список видео [{"id": "...", "title": "...", "published_at": "..."}, ...]
    """
    if not channel_id:
        channel_id = get_youtube_channel_id()
    if not api_key:
        api_key = get_youtube_api_key()
    
    if not channel_id or not api_key:
        return []
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "maxResults": max_results,
        "order": "date",
        "type": "video",
        "key": api_key
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
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
                "published_at": item["snippet"]["publishedAt"],
                "url": f"https://youtu.be/{item['id']['videoId']}"
            })
        
        log(f"Получено {len(videos)} видео")
        return videos
    except Exception as e:
        log(f"Ошибка запроса: {e}", "ERROR")
        return []

def get_video_by_id(video_id, api_key=None):
    """
    Получает информацию о конкретном видео по ID.
    
    Args:
        video_id: ID видео YouTube
        api_key: API ключ YouTube
    
    Returns:
        dict: информация о видео или None
    """
    if not api_key:
        api_key = get_youtube_api_key()
    
    if not api_key:
        return None
    
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": api_key
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        
        if "error" in data:
            log(f"API ошибка: {data['error']['message']}", "ERROR")
            return None
        
        if data.get("items"):
            item = data["items"][0]
            return {
                "id": video_id,
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "views": item["statistics"].get("viewCount", 0),
                "likes": item["statistics"].get("likeCount", 0),
                "url": f"https://youtu.be/{video_id}"
            }
        
        return None
    except Exception as e:
        log(f"Ошибка запроса: {e}", "ERROR")
        return None

def get_last_published_video_id():
    """
    Возвращает ID последнего опубликованного видео из кэша.
    Кэш хранится в файле.
    """
    cache_file = "dialogue/data/last_youtube_video.json"
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("last_video_id")
        except Exception as e:
            log(f"Ошибка чтения кэша: {e}", "ERROR")
    
    return None

def save_last_published_video_id(video_id):
    """
    Сохраняет ID последнего опубликованного видео в кэш.
    """
    cache_file = "dialogue/data/last_youtube_video.json"
    
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({
                "last_video_id": video_id,
                "updated_at": __import__('time').time()
            }, f, indent=2)
        log(f"Сохранён ID видео: {video_id}")
    except Exception as e:
        log(f"Ошибка сохранения кэша: {e}", "ERROR")

def has_new_video():
    """
    Проверяет, есть ли новое видео на канале.
    
    Returns:
        dict: новое видео или None, если новых нет
    """
    videos = get_latest_video(max_results=1)
    
    if not videos:
        log("Не удалось получить видео с канала", "WARNING")
        return None
    
    latest = videos[0]
    last_id = get_last_published_video_id()
    
    if last_id and last_id == latest["id"]:
        log(f"Новых видео нет. Последнее: {latest['title']}")
        return None
    
    log(f"🔥 НОВОЕ ВИДЕО: {latest['title']}")
    return latest

def reset_cache():
    """
    Сбрасывает кэш (принудительно обновит все видео при следующей проверке)
    """
    cache_file = "dialogue/data/last_youtube_video.json"
    if os.path.exists(cache_file):
        os.remove(cache_file)
        log("Кэш сброшен")
        return True
    return False

# Для самостоятельного тестирования
if __name__ == "__main__":
    print("=== ТЕСТ YOUTUBE AUTO ===")
    print(f"API Key: {get_youtube_api_key()[:10]}..." if get_youtube_api_key() else "API Key: None")
    print(f"Channel ID: {get_youtube_channel_id()}")
    
    videos = get_latest_video(max_results=3)
    print(f"\nПоследние видео:")
    for v in videos:
        print(f"  - {v['title']} ({v['id']})")
    
    print(f"\nПоследнее опубликованное ID: {get_last_published_video_id()}")
    new = has_new_video()
    if new:
        print(f"🔥 Есть новое видео: {new['title']}")
    else:
        print("Новых видео нет")
