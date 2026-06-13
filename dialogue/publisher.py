# ==========================================
# Файл: dialogue/publisher.py
# Справка: README.md → Публикатор
# Задача: публикация постов в TG и VK (немедленная, отложенная, из пула)
# Комментарий: VK — поддерживает группу и личку через target
# Версия: 2.0 (SQLite)
# ==========================================

import sys
import os
import json
import time
import random
import sqlite3
import threading
from datetime import datetime
from debug_utils import debug_log
from utils import escape_markdown

# ===== ЗАГРУЗКА СЕКРЕТОВ ИЗ БД =====
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.secrets_manager import get_secret
# ===================================

# ==========================================
# 1. ПУТИ К БАЗЕ ДАННЫХ
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data/ansambl.db')
CONFIG_JSON = os.path.join(PROJECT_ROOT, 'dialogue', 'data', 'config.json')  # fallback

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_posts_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            tags TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            published_at DATETIME,
            platform TEXT
        )
    ''')
    conn.commit()
    conn.close()
    debug_log("POST_POOL", "Таблица posts создана/подтверждена")

# ==========================================
# 2. РАБОТА С КОНФИГАМИ (SQLite + JSON fallback)
# ==========================================
def load_config():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT key, value FROM config")
        rows = c.fetchall()
        conn.close()
        config = {}
        for key, value in rows:
            config[key] = json.loads(value)
        if config:
            return config
    except Exception as e:
        debug_log("PUBLISH", f"Ошибка загрузки config из SQLite: {e}", "WARNING")
    
    if os.path.exists(CONFIG_JSON):
        with open(CONFIG_JSON, "r") as f:
            return json.load(f)
    return {}

def save_config_to_sqlite(config):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        for key, value in config.items():
            c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, json.dumps(value)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        debug_log("PUBLISH", f"Ошибка сохранения config: {e}", "ERROR")
        return False

# ==========================================
# 3. РАБОТА С ПУЛОМ ПОСТОВ (SQLite)
# ==========================================
def get_pending_posts():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, content, tags FROM posts WHERE status = 'pending' ORDER BY id ASC")
        rows = c.fetchall()
        conn.close()
        return [{'id': r[0], 'text': r[1], 'tags': r[2]} for r in rows]
    except Exception as e:
        debug_log("POST_POOL", f"Ошибка получения постов: {e}", "ERROR")
        return []

def add_post_to_pool(text, tags='', author='admin'):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO posts (content, tags) VALUES (?, ?)", (text, tags))
        conn.commit()
        conn.close()
        debug_log("POST_POOL", f"Пост добавлен: {text[:50]}...")
        return True
    except Exception as e:
        debug_log("POST_POOL", f"Ошибка добавления: {e}", "ERROR")
        return False

def remove_post_from_pool(post_id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()
        debug_log("POST_POOL", f"Пост {post_id} удалён")
        return True
    except Exception as e:
        debug_log("POST_POOL", f"Ошибка удаления: {e}", "ERROR")
        return False

def mark_post_published(post_id, platform='both'):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE posts SET status = 'published', published_at = ?, platform = ? WHERE id = ?",
            (datetime.now().isoformat(), platform, post_id)
        )
        conn.commit()
        conn.close()
        debug_log("POST_POOL", f"Пост {post_id} отмечен как опубликованный")
        return True
    except Exception as e:
        debug_log("POST_POOL", f"Ошибка обновления: {e}", "ERROR")
        return False

# ==========================================
# 4. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def get_random_quote():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT quote FROM quotes ORDER BY RANDOM() LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        debug_log("PUBLISH", f"Ошибка получения цитаты: {e}", "ERROR")
    return "Ритм 0,8 Гц стабилен. Сеть тлеет."

def get_auto_tags(text, platform="tg"):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT tag FROM hashtags ORDER BY RANDOM() LIMIT 5")
        rows = c.fetchall()
        conn.close()
        tags = [row[0] for row in rows]
        if tags:
            return " ".join(tags)
    except Exception as e:
        debug_log("PUBLISH", f"Ошибка получения хэштегов: {e}", "ERROR")
    return ""

# ==========================================
# 5. ПУБЛИКАЦИЯ
# ==========================================
def publish_post_immediately(bot, chat_id, text, tags_str=None, file_id=None):
    quote = get_random_quote()
    full_text = f"{text}\n\n📜 {quote}" if text else quote
    auto_tags = get_auto_tags(full_text, "tg")
    if auto_tags:
        full_text = f"{full_text}\n\n{auto_tags}"
    try:
        from services.photo_reader import get_random_post
        post = get_random_post()
        if post and post.get('photo_url'):
            bot.send_photo(chat_id, post['photo_url'], caption=full_text[:1024])
            return True
    except: pass
    try:
        bot.send_message(chat_id, full_text)
        return True
    except Exception as e:
        debug_log("PUBLISH", f"Ошибка: {e}", "ERROR")
        return False

def publish_from_pool(bot, vk_token, vk_group_id, tg_chat_id, target='group'):
    pending_posts = get_pending_posts()
    if not pending_posts:
        try:
            from dialogue.content_mixer import publish_mixed_post
            return publish_mixed_post(bot, tg_chat_id)
        except ImportError: pass
        return False
    
    post = random.choice(pending_posts)
    full_text = f"{post['text']}\n\n📜 {get_random_quote()}"
    auto_tags = get_auto_tags(full_text, "tg")
    if auto_tags:
        full_text = f"{full_text}\n\n{auto_tags}"
    
    try:
        from services.photo_reader import get_random_post
        p = get_random_post()
        photo = p.get('photo_url') if p else None
    except: photo = None
    
    success = False
    if tg_chat_id:
        try:
            if photo:
                bot.send_photo(tg_chat_id, photo, caption=full_text[:1024])
            else:
                bot.send_message(tg_chat_id, full_text)
            success = True
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка TG: {e}", "ERROR")
    
    if vk_token and vk_group_id:
        try:
            from dialogue.publisher_utils import post_to_vk
            tags = post.get('tags', '')
            sv, _ = post_to_vk(full_text, tags, vk_token, vk_group_id, target=target)
            if sv:
                success = True
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка VK: {e}", "ERROR")
    
    if success:
        mark_post_published(post['id'], 'both')
    return success

def publish_loop(bot, vk_token, vk_group_id, tg_chat_id):
    debug_log("PUBLISH", "Цикл публикации запущен (TG + VK группа)")
    while True:
        try:
            try:
                from dialogue.shabbat_manager import is_shabbat
                if is_shabbat():
                    time.sleep(3600)
                    continue
            except ImportError:
                pass
            
            config = load_config()
            interval = config.get("publisher", {}).get("interval_seconds", 7200)
            
            if publish_from_pool(bot, vk_token, vk_group_id, tg_chat_id, target='group'):
                debug_log("PUBLISH", f"Опубликовано, следующая через {interval} сек")
            else:
                debug_log("PUBLISH", "Нет постов")
            time.sleep(interval)
        except Exception as e:
            debug_log("PUBLISH", f"Ошибка в цикле: {e}", "ERROR")
            time.sleep(300)

# ==========================================
# 6. ИНИЦИАЛИЗАЦИЯ
# ==========================================
init_posts_table()
