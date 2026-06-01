# ==========================================
# Файл: services/sqlite_client.py
# Справка: README.md → SQLite клиент
# Задача: работа с SQLite (сохранение, чтение, очистка сообщений)
# ==========================================

import sqlite3
import os
from datetime import datetime
from debug_utils import debug_log

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'messages.db')

def log_sql(level, message):
    debug_log("SQLITE", message, level)

def init_db():
    """Создаёт таблицу messages, если её нет"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                text TEXT,
                timestamp TEXT,
                source TEXT
            )
        ''')
        conn.commit()
        conn.close()
        log_sql("INFO", "Таблица messages создана/подтверждена")
    except Exception as e:
        log_sql("ERROR", f"Ошибка инициализации БД: {e}")

def save_message(chat_id, text, source="tg"):
    """Сохраняет сообщение в таблицу messages"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        c.execute(
            "INSERT INTO messages (chat_id, text, timestamp, source) VALUES (?, ?, ?, ?)",
            (chat_id, text, timestamp, source)
        )
        conn.commit()
        conn.close()
        log_sql("INFO", f"Сохранено сообщение: {text[:50]}...")
    except Exception as e:
        log_sql("ERROR", f"Ошибка сохранения: {e}")

def get_messages(limit=10):
    """Возвращает последние limit сообщений"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT chat_id, text, timestamp, source FROM messages ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        messages = []
        for row in rows:
            messages.append({
                "chat_id": row[0],
                "text": row[1],
                "timestamp": row[2],
                "source": row[3]
            })
        return messages
    except Exception as e:
        log_sql("ERROR", f"Ошибка чтения: {e}")
        return []

def clean_old_messages(keep=100):
    """Удаляет сообщения старше keep последних записей"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE id NOT IN (SELECT id FROM messages ORDER BY id DESC LIMIT ?)", (keep,))
        conn.commit()
        conn.close()
        log_sql("INFO", f"Очищено сообщений (оставлено {keep})")
    except Exception as e:
        log_sql("ERROR", f"Ошибка очистки: {e}")

# Инициализация при импорте
init_db()
