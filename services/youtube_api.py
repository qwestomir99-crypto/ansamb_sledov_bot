# ==========================================
# Файл: services/youtube_api.py
# Справка: README.md → Веб-морда / YouTube прокси
# Задача: поиск, получение информации, потоковая передача YouTube видео
# Комментарий: используется в app.py для маршрутов /youtube, /youtube_search, /youtube_info, /youtube_stream
# Зависит от: yt_dlp, requests, debug_utils
# Вызывается из: services/app.py
# ==========================================

import yt_dlp
import requests
from debug_utils import debug_log

def log_proxy(level, message):
    debug_log("YOUTUBE_PROXY", message, level)

def get_youtube_info(url):
    ydl_opts = {
        'format': 'best[height<=720]',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = None
            for fmt in info.get('formats', []):
                if fmt.get('height') and fmt['height'] <= 720 and fmt.get('ext') == 'mp4':
                    if fmt.get('acodec') and fmt['acodec'] != 'none':
                        video_url = fmt['url']
                        break
            if not video_url:
                video_url = info.get('url') or info['formats'][0]['url']
            return {
                'title': info.get('title', 'YouTube видео'),
                'video_url': video_url,
                'duration': info.get('duration', 0)
            }
    except Exception as e:
        log_proxy("ERROR", f"Ошибка: {e}")
        return None

def youtube_search(query):
    """Поиск видео через Invidious API"""
    if not query:
        return []
    invidious_api = "https://yewtu.be/api/v1/search"
    try:
        resp = requests.get(invidious_api, params={
            'q': query,
            'type': 'video',
            'sort': 'relevance',
            'fields': 'videoId,title,author,viewCount,lengthSeconds,publishedText'
        }, timeout=10)
        data = resp.json()
        videos = []
        for item in data.get('items', []):
            videos.append({
                'video_url': f"https://youtube.com/watch?v={item.get('videoId')}",
                'title': item.get('title', 'Без названия'),
                'author': item.get('author', 'Неизвестный канал'),
                'views_short': item.get('viewCount', '0'),
                'duration': item.get('lengthSeconds', 0)
            })
        log_proxy("INFO", f"Поиск: {query} -> {len(videos)} видео")
        return videos[:20]
    except Exception as e:
        log_proxy("ERROR", f"Ошибка поиска: {e}")
        return []

def youtube_stream_generator(video_url):
    """Генератор для потоковой передачи видео"""
    try:
        r = requests.get(video_url, stream=True, timeout=30)
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                yield chunk
    except Exception as e:
        log_proxy("ERROR", f"Ошибка потока: {e}")
        yield b''
