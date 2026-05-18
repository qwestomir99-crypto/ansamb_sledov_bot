# ==========================================
# Модуль: services/youtube_reader.py
# Задача: читать видео с YouTube-канала, извлекать названия, описания, теги
# Зависит от: YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID в переменных окружения
# ==========================================

import os
import requests
from datetime import datetime

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID")

def get_channel_videos(max_results=5):
    """Получает последние видео с канала"""
    if not YOUTUBE_API_KEY or not YOUTUBE_CHANNEL_ID:
        print("[YOUTUBE] Не настроен API_KEY или CHANNEL_ID")
        return []
    
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
        data = r.json()
        
        if "error" in data:
            print(f"[YOUTUBE] Ошибка API: {data['error']['message']}")
            return []
        
        videos = []
        for item in data.get("items", []):
            video = {
                "id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "published_at": item["snippet"]["publishedAt"],
                "thumbnails": item["snippet"]["thumbnails"]
            }
            videos.append(video)
        
        return videos
    except Exception as e:
        print(f"[YOUTUBE] Ошибка запроса: {e}")
        return []

def get_video_details(video_id):
    """Получает детальную информацию о видео (теги, статистика)"""
    if not YOUTUBE_API_KEY:
        return None
    
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": YOUTUBE_API_KEY
    }
    
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        
        if "error" in data:
            print(f"[YOUTUBE] Ошибка API: {data['error']['message']}")
            return None
        
        items = data.get("items", [])
        if not items:
            return None
        
        item = items[0]
        return {
            "id": item["id"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "tags": item["snippet"].get("tags", []),
            "published_at": item["snippet"]["publishedAt"],
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0)),
            "comments": int(item["statistics"].get("commentCount", 0))
        }
    except Exception as e:
        print(f"[YOUTUBE] Ошибка запроса: {e}")
        return None

def get_last_video():
    """Возвращает последнее видео на канале"""
    videos = get_channel_videos(1)
    if not videos:
        return None
    return get_video_details(videos[0]["id"])

def extract_quotes_from_video(video):
    """Извлекает потенциальные цитаты из видео (название, описание)"""
    if not video:
        return []
    
    quotes = []
    
    # Название видео как цитата
    if video.get("title"):
        quotes.append({
            "source": "youtube_title",
            "text": video["title"],
            "video_id": video["id"],
            "video_url": f"https://youtu.be/{video['id']}"
        })
    
    # Первые 200 символов описания как цитата
    if video.get("description"):
        desc = video["description"].strip()
        if len(desc) > 300:
            desc = desc[:297] + "..."
        if desc:
            quotes.append({
                "source": "youtube_description",
                "text": desc,
                "video_id": video["id"],
                "video_url": f"https://youtu.be/{video['id']}"
            })
    
    return quotes

def get_video_comments(video_id, max_results=5):
    """Получает комментарии к видео (как живые цитаты)"""
    if not YOUTUBE_API_KEY:
        return []
    
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": max_results,
        "order": "relevance",
        "key": YOUTUBE_API_KEY
    }
    
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        
        if "error" in data:
            print(f"[YOUTUBE] Ошибка API комментариев: {data['error']['message']}")
            return []
        
        comments = []
        for item in data.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
        
        return comments
    except Exception as e:
        print(f"[YOUTUBE] Ошибка запроса комментариев: {e}")
        return []
