# ==========================================
# Файл: dialogue/youtube_auto.py
# Справка: README.md → YouTube автопостинг
# Задача: получение случайного видео из плейлиста YouTube
# Комментарий: видео хранятся в БД (links), кэш в SQLite
# ==========================================

import os
import random
import sqlite3
import requests
from datetime import datetime
from debug_utils import debug_log

# ===== ЗАГРУЗКА .ENV =====
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
# ===================================

# Путь к базе данных
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data/ansambl.db')
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_PLAYLIST_ID = os.getenv("YOUTUBE_PLAYLIST_ID")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_links_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            source TEXT,
            tags TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            used_at DATETIME,
            use_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    debug_log("YOUTUBE_AUTO", "Таблица links создана/подтверждена")

def get_random_video():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT url, title FROM links WHERE source = 'youtube' ORDER BY RANDOM() LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            debug_log("YOUTUBE_RANDOM", f"Выбрано случайное видео: {row[1]}")
            return {"url": row[0], "title": row[1]}
        else:
            debug_log("YOUTUBE_RANDOM", "Нет видео в базе, обновляем кэш...")
            refresh_cache()
            return get_random_video()
    except Exception as e:
        debug_log("YOUTUBE_RANDOM", f"Ошибка: {e}", "ERROR")
        return None

def add_video_to_db(url, title, tags=''):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id FROM links WHERE url = ?", (url,))
        if c.fetchone():
            conn.close()
            return False
        c.execute(
            "INSERT INTO links (url, title, source, tags, created_at) VALUES (?, ?, 'youtube', ?, ?)",
            (url, title, tags, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        debug_log("YOUTUBE_AUTO", f"Добавлено видео: {title}")
        return True
    except Exception as e:
        debug_log("YOUTUBE_AUTO", f"Ошибка добавления видео: {e}", "ERROR")
        return False

def refresh_cache():
    if not YOUTUBE_API_KEY or not YOUTUBE_PLAYLIST_ID:
        debug_log("YOUTUBE_RANDOM", "Нет API_KEY или PLAYLIST_ID", "ERROR")
        return
    
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "snippet",
        "playlistId": YOUTUBE_PLAYLIST_ID,
        "maxResults": 50,
        "key": YOUTUBE_API_KEY
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        
        if "error" in data:
            debug_log("YOUTUBE_RANDOM", f"Ошибка API: {data['error']['message']}", "ERROR")
            return
        
        items = data.get("items", [])
        if not items:
            debug_log("YOUTUBE_RANDOM", "Нет видео в плейлисте", "WARNING")
            return
        
        count = 0
        for item in items:
            snippet = item.get("snippet", {})
            video_id = snippet.get("resourceId", {}).get("videoId")
            title = snippet.get("title", "Без названия")
            if video_id:
                url = f"https://www.youtube.com/watch?v={video_id}"
                if add_video_to_db(url, title):
                    count += 1
        
        debug_log("YOUTUBE_RANDOM", f"Обновлено видео: {count} новых")
        
    except Exception as e:
        debug_log("YOUTUBE_RANDOM", f"Ошибка обновления: {e}", "ERROR")

def mark_video_used(url):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE links SET use_count = use_count + 1, used_at = ? WHERE url = ?",
            (datetime.now().isoformat(), url)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        debug_log("YOUTUBE_AUTO", f"Ошибка обновления счётчика: {e}", "ERROR")
        return False

init_links_table()
