# ==========================================
# Файл: dialogue/youtube_auto.py
# Справка: README.md → YouTube автопостинг
# Задача: выбор случайного видео из плейлиста
# Комментарий: кэширует список видео на час, не гоняется за новинками.
#              Возвращает случайное видео (id, title, url).
# Зависит от: requests, json, os, time, random
# Вызывается из: services/autoposter.py (check_and_publish)
# ==========================================

import os
import json
import random
import time
import requests

CACHE_FILE = "dialogue/data/youtube_playlist_cache.json"
CACHE_TTL = 3600  # 1 час

def log(msg, level="INFO"):
    print(f"[YOUTUBE_RANDOM] {level}: {msg}")

def get_youtube_api_key():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        log("YOUTUBE_API_KEY не задан", "ERROR")
    return api_key

def get_youtube_playlist_id():
    playlist_id = os.environ.get("YOUTUBE_PLAYLIST_ID")
    if not playlist_id:
        log("YOUTUBE_PLAYLIST_ID не задан", "ERROR")
    return playlist_id

def fetch_playlist_items(playlist_id, api_key):
    """Загружает все видео из плейлиста через YouTube API"""
    items = []
    next_page_token = None
    
    while True:
        url = "https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": api_key
        }
        if next_page_token:
            params["pageToken"] = next_page_token
        
        try:
            r = requests.get(url, params=params, timeout=15)
            data = r.json()
            
            if "error" in data:
                log(f"API ошибка: {data['error']['message']}", "ERROR")
                break
            
            for item in data.get("items", []):
                snippet = item["snippet"]
                video_id = snippet["resourceId"]["videoId"]
                items.append({
                    "id": video_id,
                    "title": snippet["title"],
                    "url": f"https://youtu.be/{video_id}"
                })
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
                
        except Exception as e:
            log(f"Ошибка запроса: {e}", "ERROR")
            break
    
    log(f"Загружено {len(items)} видео из плейлиста")
    return items

def load_cached_playlist():
    """Загружает кэш плейлиста, если он не устарел"""
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if time.time() - data.get("timestamp", 0) < CACHE_TTL:
            log(f"Загружено из кэша: {len(data['items'])} видео")
            return data["items"]
        else:
            log("Кэш устарел")
            return None
    except Exception as e:
        log(f"Ошибка чтения кэша: {e}", "ERROR")
        return None

def save_cached_playlist(items):
    """Сохраняет плейлист в кэш"""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.time(),
                "items": items
            }, f, indent=2)
        log(f"Сохранено {len(items)} видео в кэш")
    except Exception as e:
        log(f"Ошибка сохранения кэша: {e}", "ERROR")

def get_random_video():
    """
    Возвращает случайное видео из плейлиста.
    Кэширует список на CACHE_TTL секунд.
    """
    api_key = get_youtube_api_key()
    playlist_id = get_youtube_playlist_id()
    
    if not api_key or not playlist_id:
        return None
    
    # Пытаемся загрузить из кэша
    items = load_cached_playlist()
    
    if items is None:
        items = fetch_playlist_items(playlist_id, api_key)
        if items:
            save_cached_playlist(items)
        else:
            return None
    
    if not items:
        log("Плейлист пуст", "WARNING")
        return None
    
    video = random.choice(items)
    log(f"Выбрано случайное видео: {video['title']}")
    return video

# Для самостоятельного тестирования
if __name__ == "__main__":
    print("=== ТЕСТ YOUTUBE RANDOM ===")
    video = get_random_video()
    if video:
        print(f"🎬 Случайное видео: {video['title']}\n🔗 {video['url']}")
    else:
        print("❌ Не удалось получить видео")
