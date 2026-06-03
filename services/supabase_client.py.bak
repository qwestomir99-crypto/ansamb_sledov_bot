# ==========================================
# Файл: services/supabase_client.py
# Справка: README.md → База данных
# Задача: клиент для работы с Supabase (с фоллбэком на файлы)
# Комментарий: добавлена таблица analytics
# Зависит от: supabase, os, json, datetime, debug_utils
# Вызывается из: quotes.py, memory.py, posts.py, sql_analytics.py
# ==========================================

import os
import json
from datetime import datetime
from supabase import create_client, Client
from debug_utils import debug_log

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

# ==========================================
# ИНИЦИАЛИЗАЦИЯ КЛИЕНТА
# ==========================================
_supabase = None

def get_client():
    global _supabase
    if SUPABASE_URL and SUPABASE_ANON_KEY:
        if _supabase is None:
            try:
                _supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
                debug_log("SUPABASE", "Клиент инициализирован", "INFO")
            except Exception as e:
                debug_log("SUPABASE", f"Ошибка инициализации: {e}", "ERROR")
                _supabase = None
        return _supabase
    else:
        debug_log("SUPABASE", "Переменные окружения не заданы", "WARNING")
        return None

# ==========================================
# ЗАПИСЬ В БАЗУ (С ФОЛЛБЭКОМ)
# ==========================================
def db_insert(table, data, fallback_file=None):
    """
    Вставляет запись в таблицу Supabase.
    Если база недоступна — пишет в fallback_file (JSON).
    """
    client = get_client()
    if client:
        try:
            result = client.table(table).insert(data).execute()
            debug_log("SUPABASE", f"Запись в {table}: {str(data)}", "INFO")
            return result.data
        except Exception as e:
            debug_log("SUPABASE", f"Ошибка записи в {table}: {e}", "ERROR")
    
    # Фоллбэк на файл
    if fallback_file:
        try:
            fallback_data = {}
            if os.path.exists(fallback_file):
                with open(fallback_file, "r", encoding="utf-8") as f:
                    fallback_data = json.load(f)
            if "items" not in fallback_data:
                fallback_data["items"] = []
            fallback_data["items"].append(data)
            with open(fallback_file, "w", encoding="utf-8") as f:
                json.dump(fallback_data, f, indent=2)
            debug_log("SUPABASE", f"Запись в fallback {fallback_file}", "INFO")
            return [data]
        except Exception as e:
            debug_log("SUPABASE", f"Ошибка записи в fallback: {e}", "ERROR")
    return []

# ==========================================
# ЧТЕНИЕ ИЗ БАЗЫ (С ФОЛЛБЭКОМ)
# ==========================================
def db_select(table, limit=10, fallback_file=None, filter_by=None):
    """
    Читает записи из таблицы Supabase.
    Если база недоступна — читает из fallback_file (JSON).
    """
    client = get_client()
    if client:
        try:
            query = client.table(table).select("*").limit(limit)
            if filter_by:
                for key, value in filter_by.items():
                    query = query.eq(key, value)
            result = query.execute()
            debug_log("SUPABASE", f"Чтение из {table} (лимит {limit})", "INFO")
            return result.data
        except Exception as e:
            debug_log("SUPABASE", f"Ошибка чтения из {table}: {e}", "ERROR")
    
    # Фоллбэк на файл
    if fallback_file:
        try:
            with open(fallback_file, "r", encoding="utf-8") as f:
                fallback_data = json.load(f)
            items = fallback_data.get("items", [])
            debug_log("SUPABASE", f"Чтение из fallback {fallback_file}", "INFO")
            return items[-limit:]
        except Exception as e:
            debug_log("SUPABASE", f"Ошибка чтения из fallback: {e}", "ERROR")
    return []

# ==========================================
# ТАБЛИЦЫ (уже созданы через дашборд Supabase)
# ==========================================
# quotes
# memory
# posts
# analytics (новый)
