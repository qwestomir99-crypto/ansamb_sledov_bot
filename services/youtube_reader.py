# ==========================================
# Модуль: services/youtube_reader.py
# Задача: читать видео с YouTube-канала, извлекать названия, описания, теги
# Зависит от: YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID в переменных окружения
# Комментарий: все действия логируются, ошибки не роняют бота
# ==========================================

import os
import requests
import time
from datetime import datetime

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID")

def log(msg, level="INFO"):
    """Единый формат логов для YouTube модуля"""
    print(f"[YOUTUBE] {level}: {msg}")

def get_channel_videos(max_results=5):
    """Получает последние видео с канала"""
    if not YOUTUBE_API_KEY:
        log("API ключ не настроен (YOUTUBE_API_KEY отсутствует)", "WARNING")
        return []
    
    if not YOUTUBE_CHANNEL_ID:
        log("ID канала не настроен (YOUTUBE_CHANNEL_ID отсутствует)", "WARNING")
        return []
    
    log(f"Запрос последних {max_results} видео с канала {YOUTUBE_CHANNEL_ID}")
    
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
        start_time = time.time()
        r = requests.get(url, params=params, timeout=10)
        elapsed = time.time() - start_time
        log(f"Запрос выполнен за {elapsed:.2f} сек, статус {r.status_code}")
        
        if r.status_code != 200:
            log(f"HTTP ошибка: {r.status_code}", "ERROR")
            return []
        
        data = r.json()
        
        if "error" in data:
            log(f"API ошибка: {data['error']['message']}", "ERROR")
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
        
        log(f"Получено {len(videos)} видео")
        return videos
    except requests.exceptions.Timeout:
        log("Таймаут при запросе к YouTube API", "ERROR")
        return []
    except requests.exceptions.ConnectionError:
        log("Ошибка соединения с YouTube API", "ERROR")
        return []
    except Exception as e:
        log(f"Неизвестная ошибка: {type(e).__name__} - {e}", "ERROR")
        return []

def get_video_details(video_id):
    """Получает детальную информацию о видео (теги, статистика)"""
    if not YOUTUBE_API_KEY:
        log("API ключ не настроен", "WARNING")
        return None
    
    log(f"Запрос деталей видео {video_id}")
    
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": YOUTUBE_API_KEY
    }
    
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            log(f"HTTP ошибка при получении деталей: {r.status_code}", "ERROR")
            return None
        
        data = r.json()
        
        if "error" in data:
            log(f"API ошибка: {data['error']['message']}", "ERROR")
            return None
        
        items = data.get("items", [])
        if not items:
            log(f"Видео {video_id} не найдено", "WARNING")
            return None
        
        item = items[0]
        result = {
            "id": item["id"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "tags": item["snippet"].get("tags", []),
            "published_at": item["snippet"]["publishedAt"],
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0)),
            "comments": int(item["statistics"].get("commentCount", 0))
        }
        log(f"Детали получены: {result['title']}, просмотров {result['views']}")
        return result
    except Exception as e:
        log(f"Ошибка при получении деталей: {type(e).__name__} - {e}", "ERROR")
        return None

def get_last_video():
    """Возвращает последнее видео на канале"""
    log("Поиск последнего видео...")
    videos = get_channel_videos(1)
    if not videos:
        log("Видео не найдены", "WARNING")
        return None
    
    video_id = videos[0]["id"]
    log(f"Последнее видео: {video_id}")
    return get_video_details(video_id)

def extract_quotes_from_video(video):
    """Извлекает потенциальные цитаты из видео (название, описание)"""
    if not video:
        log("Видео пустое, цитаты не извлечены", "WARNING")
        return []
    
    quotes = []
    
    # Название видео как цитата
    if video.get("title"):
        quote_text = f"📺 {video['title']}\n🔗 https://youtu.be/{video['id']}"
        quotes.append({
            "source": "youtube_title",
            "text": quote_text,
            "video_id": video["id"],
            "video_url": f"https://youtu.be/{video['id']}"
        })
        log(f"Извлечена цитата из названия: {video['title'][:50]}...")
    
    # Первые 300 символов описания как цитата
    if video.get("description"):
        desc = video["description"].strip()
        if len(desc) > 300:
            desc = desc[:297] + "..."
        if desc:
            quote_text = f"📺 {desc}\n🔗 https://youtu.be/{video['id']}"
            quotes.append({
                "source": "youtube_description",
                "text": quote_text,
                "video_id": video["id"],
                "video_url": f"https://youtu.be/{video['id']}"
            })
            log(f"Извлечена цитата из описания: {desc[:50]}...")
    
    log(f"Всего извлечено {len(quotes)} цитат из видео")
    return quotes

def get_video_comments(video_id, max_results=5):
    """Получает комментарии к видео (как живые цитаты)"""
    if not YOUTUBE_API_KEY:
        log("API ключ не настроен", "WARNING")
        return []
    
    log(f"Запрос комментариев к видео {video_id}")
    
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
        if r.status_code != 200:
            log(f"HTTP ошибка при получении комментариев: {r.status_code}", "ERROR")
            return []
        
        data = r.json()
        
        if "error" in data:
            log(f"API ошибка: {data['error']['message']}", "ERROR")
            return []
        
        comments = []
        for item in data.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
        
        log(f"Получено {len(comments)} комментариев")
        return comments
    except Exception as e:
        log(f"Ошибка при получении комментариев: {type(e).__name__} - {e}", "ERROR")
        return []

# Функция для проверки работоспособности (можно вызывать вручную)
def test_youtube_connection():
    """Тест подключения к YouTube API"""
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
        log(f"✅ Последнее видео найдено: {video['title']}")
        return True
    else:
        log("❌ Не удалось получить видео", "ERROR")
        return False

if __name__ == "__main__":
    # Позволяет запустить тест напрямую
    test_youtube_connection()
