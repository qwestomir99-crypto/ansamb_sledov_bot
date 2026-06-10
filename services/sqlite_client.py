# ==========================================
# Файл: services/sqlite_client.py
# Справка: README.md → PostgreSQL клиент
# Задача: работа с PostgreSQL (сообщения + цитаты + конфиг)
# Комментарий: переход с SQLite на PostgreSQL для стабильности на Bothost
# ==========================================

import os
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from debug_utils import debug_log

DATABASE_URL = os.environ.get("DATABASE_URL")
QUOTES_FALLBACK_FILE = "dialogue/data/quotes.txt"

def log_db(level, message):
    debug_log("POSTGRES", message, level)

def get_connection():
    """Создаёт подключение к PostgreSQL"""
    if not DATABASE_URL:
        raise Exception("DATABASE_URL не задан")
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Создаёт все таблицы, если их нет"""
    try:
        conn = get_connection()
        c = conn.cursor()
        
        # Таблица сообщений
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT,
                text TEXT,
                timestamp TEXT,
                source TEXT
            )
        ''')
        
        # Таблица цитат
        c.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id SERIAL PRIMARY KEY,
                text TEXT NOT NULL,
                created_at TEXT
            )
        ''')
        
        # Таблица конфига
        c.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value JSONB NOT NULL
            )
        ''')
        
        # Таблица состояния адаптивных режимов
        c.execute('''
            CREATE TABLE IF NOT EXISTS adaptive_state (
                id INTEGER PRIMARY KEY DEFAULT 1,
                last_switch DOUBLE PRECISION DEFAULT 0,
                current_adaptive_mode TEXT,
                deadend_count INTEGER DEFAULT 0,
                last_return_to_etalon DOUBLE PRECISION DEFAULT 0
            )
        ''')
        
        # Вставляем дефолтное состояние, если пусто
        c.execute("SELECT COUNT(*) FROM adaptive_state")
        if c.fetchone()[0] == 0:
            c.execute('''
                INSERT INTO adaptive_state (id, last_switch, deadend_count, last_return_to_etalon)
                VALUES (1, 0, 0, 0)
            ''')
        
        conn.commit()
        conn.close()
        log_db("INFO", "Таблицы созданы/подтверждены")
        migrate_quotes()
    except Exception as e:
        log_db("ERROR", f"Ошибка инициализации: {e}")

# ==========================================
# СООБЩЕНИЯ
# ==========================================
def save_message(chat_id, text, source="tg"):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO messages (chat_id, text, timestamp, source) VALUES (%s, %s, %s, %s)",
            (chat_id, text, datetime.now().isoformat(), source)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log_db("ERROR", f"Ошибка save_message: {e}")

def get_messages(limit=10):
    try:
        conn = get_connection()
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT chat_id, text, timestamp, source FROM messages ORDER BY id DESC LIMIT %s", (limit,))
        rows = c.fetchall()
        conn.close()
        return [{"chat_id": r["chat_id"], "text": r["text"], "timestamp": r["timestamp"], "source": r["source"]} for r in rows]
    except Exception as e:
        log_db("ERROR", f"Ошибка get_messages: {e}")
        return []

def clean_old_messages(keep=100):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE id NOT IN (SELECT id FROM messages ORDER BY id DESC LIMIT %s)", (keep,))
        conn.commit()
        conn.close()
    except Exception as e:
        log_db("ERROR", f"Ошибка clean: {e}")

# ==========================================
# ЦИТАТЫ
# ==========================================
def migrate_quotes():
    """Переносит цитаты из quotes.txt в PostgreSQL, если таблица пуста"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM quotes")
        count = c.fetchone()[0]
        conn.close()
        
        if count == 0 and os.path.exists(QUOTES_FALLBACK_FILE):
            with open(QUOTES_FALLBACK_FILE, "r", encoding="utf-8") as f:
                quotes = [line.strip() for line in f.readlines() if line.strip()]
            conn = get_connection()
            c = conn.cursor()
            for quote in quotes:
                c.execute("INSERT INTO quotes (text, created_at) VALUES (%s, %s)", (quote, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            log_db("INFO", f"Мигрировано {len(quotes)} цитат из файла")
    except Exception as e:
        log_db("ERROR", f"Ошибка миграции цитат: {e}")

def get_quotes(limit=10):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT text FROM quotes ORDER BY id DESC LIMIT %s", (limit,))
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        log_db("ERROR", f"Ошибка get_quotes: {e}")
        if os.path.exists(QUOTES_FALLBACK_FILE):
            with open(QUOTES_FALLBACK_FILE, "r", encoding="utf-8") as f:
                return [line.strip() for line in f.readlines() if line.strip()][-limit:]
        return []

def get_quotes_list():
    return get_quotes(10000)

def add_quote(text):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO quotes (text, created_at) VALUES (%s, %s)", (text, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_db("ERROR", f"Ошибка add_quote: {e}")
        try:
            with open(QUOTES_FALLBACK_FILE, "a", encoding="utf-8") as f:
                f.write(text + "\n")
            return True
        except:
            return False

def delete_quote_by_id(quote_id):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM quotes WHERE id = %s", (quote_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_db("ERROR", f"Ошибка delete_quote: {e}")
        return False

# ==========================================
# КОНФИГ
# ==========================================
def load_config_from_db():
    """Загружает конфиг из PostgreSQL"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT value FROM config WHERE key = 'main'")
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]
        return None
    except Exception as e:
        log_db("ERROR", f"Ошибка загрузки конфига: {e}")
        return None

def save_config_to_db(config):
    """Сохраняет конфиг в PostgreSQL"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO config (key, value) VALUES ('main', %s) ON CONFLICT (key) DO UPDATE SET value = %s",
            (json.dumps(config), json.dumps(config))
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_db("ERROR", f"Ошибка сохранения конфига: {e}")
        return False

# ==========================================
# АДАПТИВНОЕ СОСТОЯНИЕ
# ==========================================
def load_adaptive_state():
    """Загружает состояние адаптивных режимов из PostgreSQL"""
    try:
        conn = get_connection()
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT * FROM adaptive_state WHERE id = 1")
        row = c.fetchone()
        conn.close()
        if row:
            return {
                "last_switch": row["last_switch"],
                "current_adaptive_mode": row["current_adaptive_mode"],
                "deadend_count": row["deadend_count"],
                "last_return_to_etalon": row["last_return_to_etalon"]
            }
        return {"last_switch": 0, "current_adaptive_mode": None, "deadend_count": 0, "last_return_to_etalon": 0}
    except Exception as e:
        log_db("ERROR", f"Ошибка загрузки adaptive_state: {e}")
        return {"last_switch": 0, "current_adaptive_mode": None, "deadend_count": 0, "last_return_to_etalon": 0}

def save_adaptive_state(state):
    """Сохраняет состояние адаптивных режимов в PostgreSQL"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE adaptive_state SET last_switch = %s, current_adaptive_mode = %s, deadend_count = %s, last_return_to_etalon = %s WHERE id = 1",
            (state.get("last_switch", 0), state.get("current_adaptive_mode"), state.get("deadend_count", 0), state.get("last_return_to_etalon", 0))
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_db("ERROR", f"Ошибка сохранения adaptive_state: {e}")
        return False

# Инициализация
init_db()
