# ==========================================
# Файл: services/sqlite_client.py
# Справка: README.md → SQLite клиент
# Задача: работа с SQLite (сообщения + цитаты)
# ==========================================

import sqlite3
import os
from datetime import datetime
from debug_utils import debug_log

MSG_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'messages.db')
QUOTES_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'quotes.db')
QUOTES_FALLBACK_FILE = "dialogue/data/quotes.txt"

def log_sql(level, message):
    debug_log("SQLITE", message, level)

# ==========================================
# СООБЩЕНИЯ
# ==========================================
def init_msg_db():
    try:
        conn = sqlite3.connect(MSG_DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, text TEXT, timestamp TEXT, source TEXT)''')
        conn.commit()
        conn.close()
        log_sql("INFO", "Таблица messages создана/подтверждена")
    except Exception as e:
        log_sql("ERROR", f"Ошибка messages: {e}")

def save_message(chat_id, text, source="tg"):
    try:
        conn = sqlite3.connect(MSG_DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO messages (chat_id, text, timestamp, source) VALUES (?, ?, ?, ?)", (chat_id, text, datetime.now().isoformat(), source))
        conn.commit()
        conn.close()
    except Exception as e:
        log_sql("ERROR", f"Ошибка save_message: {e}")

def get_messages(limit=10):
    try:
        conn = sqlite3.connect(MSG_DB_PATH)
        c = conn.cursor()
        c.execute("SELECT chat_id, text, timestamp, source FROM messages ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [{"chat_id": r[0], "text": r[1], "timestamp": r[2], "source": r[3]} for r in rows]
    except: return []

def clean_old_messages(keep=100):
    try:
        conn = sqlite3.connect(MSG_DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE id NOT IN (SELECT id FROM messages ORDER BY id DESC LIMIT ?)", (keep,))
        conn.commit()
        conn.close()
    except Exception as e:
        log_sql("ERROR", f"Ошибка clean: {e}")

# ==========================================
# ЦИТАТЫ
# ==========================================
def init_quotes_db():
    try:
        os.makedirs(os.path.dirname(QUOTES_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(QUOTES_DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, created_at TEXT)''')
        conn.commit()
        conn.close()
        log_sql("INFO", "Таблица quotes создана/подтверждена")
        migrate_quotes()
    except Exception as e:
        log_sql("ERROR", f"Ошибка quotes: {e}")

def migrate_quotes():
    try:
        conn = sqlite3.connect(QUOTES_DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM quotes")
        count = c.fetchone()[0]
        conn.close()
        if count == 0 and os.path.exists(QUOTES_FALLBACK_FILE):
            with open(QUOTES_FALLBACK_FILE, "r", encoding="utf-8") as f:
                quotes = [line.strip() for line in f.readlines() if line.strip()]
            conn = sqlite3.connect(QUOTES_DB_PATH)
            c = conn.cursor()
            for quote in quotes:
                c.execute("INSERT INTO quotes (text, created_at) VALUES (?, ?)", (quote, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            log_sql("INFO", f"Мигрировано {len(quotes)} цитат")
    except Exception as e:
        log_sql("ERROR", f"Ошибка миграции: {e}")

def get_quotes(limit=10):
    try:
        conn = sqlite3.connect(QUOTES_DB_PATH)
        c = conn.cursor()
        c.execute("SELECT text FROM quotes ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]
    except:
        if os.path.exists(QUOTES_FALLBACK_FILE):
            with open(QUOTES_FALLBACK_FILE, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines() if line.strip()][-limit:]
        return []

def get_quotes_list():
    return get_quotes(10000)

def add_quote(text):
    try:
        conn = sqlite3.connect(QUOTES_DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO quotes (text, created_at) VALUES (?, ?)", (text, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except:
        try:
            with open(QUOTES_FALLBACK_FILE, "a", encoding="utf-8") as f: f.write(text + "\n")
            return True
        except: return False

def delete_quote_by_id(quote_id):
    try:
        conn = sqlite3.connect(QUOTES_DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
        conn.commit()
        conn.close()
        return True
    except: return False

# Инициализация
init_msg_db()
init_quotes_db()
