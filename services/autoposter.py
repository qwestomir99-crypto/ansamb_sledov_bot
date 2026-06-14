# ==========================================
# Файл: services/autoposter.py
# Справка: README.md → Автопостер YouTube
# Задача: автоматически постить видео из плейлиста в TG и VK
# Комментарий: защищён от байтов и кривых данных
# ==========================================

import os
import time
import threading
import requests
from datetime import datetime
from debug_utils import debug_log

# ==========================================
# ЗАЩИТНЫЕ ФУНКЦИИ
# ==========================================

def ensure_string(value, default=""):
    if value is None:
        return default
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin1')
    return str(value)

def ensure_int(value, default=0):
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        if isinstance(value, str):
            import re
            numbers = re.findall(r'-?\d+', value)
            if numbers:
                return int(numbers[0])
        return default

# ==========================================
# ОСНОВНЫЕ ФУНКЦИИ
# ==========================================

def log_ap(level, message):
    debug_log("AUTOPOSTER", message, level)

def get_vk_token():
    token = os.getenv("VK_TOKEN")
    return ensure_string(token)

def get_vk_group_id():
    group_id = os.getenv("VK_GROUP_ID")
    return ensure_int(group_id)

def get_tg_chat_id():
    chat_id = os.getenv("TG_CHAT_ID", "@qwestomir")
    return ensure_string(chat_id)

def get_playlist_id():
    playlist = os.getenv("YOUTUBE_PLAYLIST_ID")
    return ensure_string(playlist)

def get_api_key():
    api_key = os.getenv("YOUTUBE_API_KEY")
    return ensure_string(api_key)

def fetch_latest_video():
    api_key = get_api_key()
    playlist_id = get_playlist_id()
    if not api_key or not playlist_id:
        log_ap("ERROR", "Нет API ключа или ID плейлиста")
        return None
    
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=1&playlistId={playlist_id}&key={api_key}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if 'items' in data and data['items']:
            item = data['items'][0]
            video_id = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            return {'id': video_id, 'title': title}
        log_ap("WARNING", "Нет видео в плейлисте")
        return None
    except Exception as e:
        log_ap("ERROR", f"Ошибка получения видео: {e}")
        return None

def send_to_tg(video_id, title):
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = get_tg_chat_id()
    if not bot_token or not chat_id:
        log_ap("ERROR", "Нет токена бота или chat_id")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    message = f"🎬 {title}\nhttps://www.youtube.com/watch?v={video_id}"
    try:
        r = requests.post(url, data={'chat_id': chat_id, 'text': message}, timeout=10)
        if r.status_code == 200:
            log_ap("INFO", f"Видео отправлено в TG: {title}")
            return True
        log_ap("ERROR", f"Ошибка TG: {r.status_code} - {r.text}")
        return False
    except Exception as e:
        log_ap("ERROR", f"Ошибка отправки в TG: {e}")
        return False

def send_to_vk(video_id, title):
    token = get_vk_token()
    group_id = get_vk_group_id()
    if not token or not group_id:
        log_ap("ERROR", "Нет токена VK или ID группы")
        return False
    
    message = f"🎬 {title}\nhttps://www.youtube.com/watch?v={video_id}"
    params = {
        'access_token': token,
        'v': '5.199',
        'owner_id': -group_id,
        'from_group': 1,
        'message': message
    }
    try:
        r = requests.post('https://api.vk.com/method/wall.post', params=params, timeout=10)
        data = r.json()
        if 'response' in data:
            log_ap("INFO", f"Видео отправлено в VK: {title}")
            return True
        log_ap("ERROR", f"Ошибка VK: {data.get('error', {}).get('error_msg', 'неизвестно')}")
        return False
    except Exception as e:
        log_ap("ERROR", f"Ошибка отправки в VK: {e}")
        return False

def autoposter_loop():
    last_video_id = None
    while True:
        try:
            video = fetch_latest_video()
            if video:
                video_id = video['id']
                if video_id != last_video_id:
                    log_ap("INFO", f"Новое видео: {video['title']}")
                    send_to_tg(video_id, video['title'])
                    send_to_vk(video_id, video['title'])
                    last_video_id = video_id
            time.sleep(3600)  # проверка раз в час
        except Exception as e:
            log_ap("ERROR", f"Ошибка в цикле: {e}")
            time.sleep(3600)

def start_autoposter(config=None, vk_token=None, vk_group_id=None):
    thread = threading.Thread(target=autoposter_loop, daemon=True)
    thread.start()
    log_ap("INFO", "Автопостер YouTube запущен (TG + VK)")

if __name__ == "__main__":
    print("Автопостер YouTube готов к работе")
