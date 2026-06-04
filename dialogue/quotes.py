# ==========================================
# Модуль: dialogue/quotes.py
# Справка: README.md → Цитаты
# Задача: публикация цитат по расписанию + проверка шаббата
# Комментарий: ИСПОЛЬЗУЕТ ВНУТРЕННЮЮ SQLITE (без внешнего Supabase)
# ==========================================

import time
import random
import os
import json
import sqlite3
from datetime import datetime
import threading
from debug_utils import debug_log
from dialogue.activity_modes import should_publish_quotes, get_quotes_interval, load_config

# ==========================================
# КОНСТАНТЫ
# ==========================================
CONFIG_FILE = "config.json"
QUOTES_FALLBACK_FILE = "dialogue/data/quotes.txt"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'quotes.db')

# ==========================================
# ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ
# ==========================================
def init_db():
    """Создаёт таблицу quotes, если её нет"""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
        debug_log("QUOTES", "Таблица quotes создана/подтверждена")
        migrate_from_file()
    except Exception as e:
        debug_log("QUOTES", f"Ошибка инициализации БД: {e}", "ERROR")

def migrate_from_file():
    """Переносит цитаты из файла в SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM quotes")
        count = c.fetchone()[0]
        conn.close()
        
        if count == 0 and os.path.exists(QUOTES_FALLBACK_FILE):
            with open(QUOTES_FALLBACK_FILE, "r", encoding="utf-8") as f:
                quotes = [line.strip() for line in f.readlines() if line.strip()]
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            for quote in quotes:
                c.execute("INSERT INTO quotes (text, created_at) VALUES (?, ?)", 
                          (quote, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            debug_log("QUOTES", f"Мигрировано {len(quotes)} цитат из файла")
    except Exception as e:
        debug_log("QUOTES", f"Ошибка миграции: {e}", "ERROR")

# ==========================================
# РАБОТА С ЦИТАТАМИ
# ==========================================
def get_quotes(limit=10):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT text FROM quotes ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [row[0] for row in rows]
    except Exception as e:
        debug_log("QUOTES", f"Ошибка чтения цитат из БД: {e}", "ERROR")
        if os.path.exists(QUOTES_FALLBACK_FILE):
            with open(QUOTES_FALLBACK_FILE, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines() if line.strip()][-limit:]
        return []

def get_all_quotes():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, text, created_at FROM quotes ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        return [{"id": row[0], "text": row[1], "created_at": row[2]} for row in rows]
    except Exception as e:
        debug_log("QUOTES", f"Ошибка: {e}", "ERROR")
        return []

def add_quote(text):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO quotes (text, created_at) VALUES (?, ?)", 
                  (text, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        debug_log("QUOTES", f"Цитата добавлена: {text[:50]}...")
        return True
    except Exception as e:
        debug_log("QUOTES", f"Ошибка добавления цитаты: {e}", "ERROR")
        try:
            with open(QUOTES_FALLBACK_FILE, "a", encoding="utf-8") as f:
                f.write(text + "\n")
            return True
        except:
            return False

def delete_quote_by_id(quote_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        debug_log("QUOTES", f"Ошибка удаления: {e}", "ERROR")
        return False

def get_quotes_list():
    return get_quotes(10000)

def get_quotes_interval_minutes():
    config = load_config()
    return config.get("quotes", {}).get("interval_minutes", 60)

def set_quotes_interval_minutes(minutes):
    config = load_config()
    if "quotes" not in config:
        config["quotes"] = {}
    config["quotes"]["interval_minutes"] = minutes
    save_config(config)

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def set_quotes_interval(minutes):
    return set_quotes_interval_minutes(minutes)

def get_quotes_interval():
    return get_quotes_interval_minutes()

# ==========================================
# ОТПРАВКА ЦИТАТЫ С ФОТО
# ==========================================
def send_quote_with_photo(bot, chat_id, quote):
    try:
        from services.photo_reader import get_random_post
        post = get_random_post()
        if post and post.get('photo_url'):
            caption = post['text']
            if len(caption) + len(quote) + 50 < 1024:
                caption += f"\n\n📜 {quote}"
            tags = ' '.join(post.get('tags', [])[:3])
            if len(caption) + len(tags) + 10 < 1024:
                caption += f"\n\n{tags}"
            caption = caption[:1024]
            bot.send_photo(chat_id, post['photo_url'], caption=caption, parse_mode='Markdown')
            debug_log("QUOTES", f"Цитата отправлена с фото")
            return True
        else:
            bot.send_message(chat_id, f"📜 *Цитата дня* • {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n{quote}\n\n#ЦитатаДня #СапёрыАутентичности", parse_mode='Markdown')
            return False
    except Exception as e:
        debug_log("QUOTES", f"Ошибка отправки цитаты с фото: {e}", "ERROR")
        bot.send_message(chat_id, f"📜 *Цитата дня* • {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n{quote}\n\n#ЦитатаДня #СапёрыАутентичности", parse_mode='Markdown')
        return False

# ==========================================
# ЦИКЛ ПУБЛИКАЦИИ ЦИТАТ (с шаббатом)
# ==========================================
quote_thread_running = False
quote_thread = None

def quotes_loop(bot, TG_CHAT_ID):
    global quote_thread_running, quote_thread
    
    quote_thread_running = False
    if quote_thread and quote_thread.is_alive():
        time.sleep(1)
    
    quote_thread_running = True
    
    def _run():
        last_interval = None
        
        while quote_thread_running:
            # Проверка шаббата
            try:
                from dialogue.shabbat_manager import is_shabbat
                if is_shabbat():
                    debug_log("QUOTES", "Шаббат — цитаты отдыхают")
                    time.sleep(3600)
                    continue
            except ImportError:
                pass
            
            if not should_publish_quotes():
                time.sleep(60)
                continue
            
            base_interval = get_quotes_interval()
            current_interval = base_interval
            
            if current_interval != last_interval:
                last_interval = current_interval
                debug_log("QUOTES", f"Интервал обновлён: {current_interval} минут")
            
            if current_interval <= 0:
                time.sleep(60)
                continue
            
            interval_seconds = current_interval * 60
            time.sleep(interval_seconds)
            
            if not quote_thread_running or not should_publish_quotes():
                continue
            
            # Повторная проверка шаббата перед отправкой
            try:
                from dialogue.shabbat_manager import is_shabbat
                if is_shabbat():
                    continue
            except ImportError:
                pass
                
            quotes = get_quotes()
            if not quotes:
                continue
                
            quote = random.choice(quotes)
            send_quote_with_photo(bot, TG_CHAT_ID, quote)
            debug_log("QUOTES", f"Цитата отправлена (интервал {current_interval} мин)")
    
    quote_thread = threading.Thread(target=_run, daemon=True)
    quote_thread.start()
    debug_log("QUOTES", "Цитаты запущены (SQLite + шаббат)")

#==================================
#   ютуб линки
#==================================
def send_quote_with_photo(bot, chat_id, quote):
    """Отправляет цитату с YouTube-видео из плейлиста"""
    try:
        from dialogue.youtube_auto import get_random_video
        
        video = get_random_video()
        if video and video.get('url'):
            caption = f"📜 {quote}\n\n🎬 {video['title']}\n{video['url']}"
            if len(caption) > 1024:
                caption = f"📜 {quote}\n\n🎬 {video['title']}\n{video['url']}"
                caption = caption[:1024]
            
            bot.send_message(chat_id, caption, parse_mode='Markdown')
            debug_log("QUOTES", f"Цитата отправлена с YouTube-видео")
            return True
        else:
            # Фоллбэк на просто текст
            bot.send_message(chat_id, f"📜 *Цитата* • {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n{quote}\n\n#Цитата #СапёрыАутентичности", parse_mode='Markdown')
            return False
    except Exception as e:
        debug_log("QUOTES", f"Ошибка отправки цитаты с видео: {e}", "ERROR")
        bot.send_message(chat_id, f"📜 *Цитата* • {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n{quote}\n\n#Цитата #СапёрыАутентичности", parse_mode='Markdown')
        return False
        
init_db()
