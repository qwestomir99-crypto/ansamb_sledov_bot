# ==========================================
# Файл: Alice/response_cache.py
# Справка: README.md → Алиса / Кэш ответов
# Задача: кэширование ответов Алисы в Supabase
# Комментарий: снижает нагрузку на Yandex GPT, ускоряет повторные ответы
# Зависит от: services.supabase_client, hashlib, json, datetime
# Вызывается из: Alice/core.py (generate_alice_response)
# ==========================================

import hashlib
import json
from datetime import datetime
from services.supabase_client import db_insert, db_select

CACHE_TABLE = "alice_cache"
CACHE_TTL = 3600  # 1 час

def log_cache(level, message):
    debug_log("ALICE_CACHE", message, level)

def _generate_hash(query, role, mood):
    """Генерирует уникальный хэш для запроса."""
    data = f"{query}|{role}|{mood}"
    return hashlib.md5(data.encode()).hexdigest()

def get_cached_response(query, role, mood):
    """Возвращает закэшированный ответ, если он есть и не устарел."""
    query_hash = _generate_hash(query, role, mood)
    result = db_select(CACHE_TABLE, limit=1, filter_by={"query_hash": query_hash})
    
    if result:
        cached = result[0]
        created_at = datetime.fromisoformat(cached.get("created_at"))
        if (datetime.now() - created_at).total_seconds() < CACHE_TTL:
            log_cache("INFO", f"Найден кэш для запроса: {query[:50]}...")
            return cached.get("response")
    return None

def save_cached_response(query, role, mood, response):
    """Сохраняет ответ в кэш."""
    query_hash = _generate_hash(query, role, mood)
    data = {
        "query_hash": query_hash,
        "role": role,
        "mood": mood,
        "response": response,
        "created_at": datetime.now().isoformat()
    }
    db_insert(CACHE_TABLE, data)
    log_cache("INFO", f"Сохранён кэш для запроса: {query[:50]}...")
