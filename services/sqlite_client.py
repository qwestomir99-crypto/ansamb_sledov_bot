#!/usr/bin/env python3
# ==========================================
# Файл: services/sqlite_client.py
# Справка: README.md → SQLite клиент для TimeWeb
# Задача: работа с цитатами, сообщениями, конфигом через SQLite
# Комментарий: адаптировано для TimeWeb, используется data/ansambl.db
# ==========================================

import sys
import os
import sqlite3
import json
from datetime import datetime

# ===== ФИКС ПУТИ К БИБЛИОТЕКАМ =====
sys.path.insert(0, '/home/c/ch756438/.local/lib/python3.10/site-packages')
# ===================================

from debug_utils import debug_log

# Путь к единой базе данных
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data/ansambl.db')

def log_db(level, message):
    debug_log("SQLITE", message, level)

def get_connection():
    """Создаёт подключение к SQLite, создаёт папку при необходимости"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Создаёт все необходимые таблицы, если их нет"""
    try:
        conn = get_connection()
        c = conn.cursor()
        
        # Таблица цитат
        c.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote TEXT NOT NULL,
                created_at TEXT
            )
        ''')
        
        # Таблица сообщений (опционально)
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                text TEXT,
                timestamp TEXT,
                source TEXT
            )
        ''')
        
        # Таблица конфига (ключ-значение)
        c.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        log_db("INFO", "Таблицы созданы/подтверждены")
    except Exception as e:
        log_db("ERROR", f"Ошибка инициализации: {e}")

# ==========================================
# СООБЩЕНИЯ (опционально)
# ==========================================
def save_message(chat_id, text, source="tg"):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO messages (chat_id, text, timestamp, source) VALUES (?, ?, ?, ?)",
            (chat_id, text, datetime.now().isoformat(), source)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log_db("ERROR", f"Ошибка save_message: {e}")

def get_messages(limit=10):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT chat_id, text, timestamp, source FROM messages ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [{"chat_id": r[0], "text": r[1], "timestamp": r[2], "source": r[3]} for r in rows]
    except Exception as e:
        log_db("ERROR", f"Ошибка get_messages: {e}")
        return []

def clean_old_messages(keep=100):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE id NOT IN (SELECT id FROM messages ORDER BY id DESC LIMIT ?)", (keep,))
        conn.commit()
        conn.close()
    except Exception as e:
        log_db("ERROR", f"Ошибка clean: {e}")

# ==========================================
# ЦИТАТЫ
# ==========================================
def get_quotes(limit=10):
    """Возвращает последние N цитат"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT quote FROM quotes ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        log_db("ERROR", f"Ошибка get_quotes: {e}")
        return []

def get_quotes_list():
    """Возвращает все цитаты"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT quote FROM quotes ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        log_db("ERROR", f"Ошибка get_quotes_list: {e}")
        return []

def add_quote(text):
    """Добавляет новую цитату"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO quotes (quote, created_at) VALUES (?, ?)", (text, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        log_db("INFO", f"Цитата добавлена: {text[:50]}...")
        return True
    except Exception as e:
        log_db("ERROR", f"Ошибка add_quote: {e}")
        return False

def delete_quote_by_id(quote_id):
    """Удаляет цитату по ID"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_db("ERROR", f"Ошибка delete_quote: {e}")
        return False

# ==========================================
# КОНФИГ (ключ-значение)
# ==========================================
def load_config_from_db():
    """Загружает конфиг из таблицы config (ключ 'main')"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT value FROM config WHERE key = 'main'")
        row = c.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return None
    except Exception as e:
        log_db("ERROR", f"Ошибка загрузки конфига: {e}")
        return None

def save_config_to_db(config):
    """Сохраняет конфиг в таблицу config (ключ 'main')"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES ('main', ?)",
            (json.dumps(config),)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_db("ERROR", f"Ошибка сохранения конфига: {e}")
        return False

# ==========================================
# АДАПТИВНОЕ СОСТОЯНИЕ (опционально)
# ==========================================
def load_adaptive_state():
    """Загружает состояние адаптивных режимов"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT value FROM config WHERE key = 'adaptive_state'")
        row = c.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return {"last_switch": 0, "current_adaptive_mode": None, "deadend_count": 0, "last_return_to_etalon": 0}
    except Exception as e:
        log_db("ERROR", f"Ошибка load_adaptive_state: {e}")
        return {"last_switch": 0, "current_adaptive_mode": None, "deadend_count": 0, "last_return_to_etalon": 0}

def save_adaptive_state(state):
    """Сохраняет состояние адаптивных режимов"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES ('adaptive_state', ?)",
            (json.dumps(state),)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_db("ERROR", f"Ошибка save_adaptive_state: {e}")
        return False

# Инициализация базы данных при загрузке модуля
init_db()
