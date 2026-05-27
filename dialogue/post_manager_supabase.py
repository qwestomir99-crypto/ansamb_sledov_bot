# ==========================================
# Модуль: dialogue/post_manager_supabase.py
# Справка: README.md → Управление постами
# Задача: управление постами (добавление, редактирование, удаление)
# Комментарий: использует Supabase с фоллбэком на post_pool.json
# Зависит от: json, os, datetime, services.supabase_client, debug_utils
# Вызывается из: admin_commands.py, publisher.py
# ==========================================

import os
import json
from datetime import datetime
from debug_utils import debug_log
from services.supabase_client import db_insert, db_select

# ==========================================
# КОНСТАНТЫ
# ==========================================
POSTS_TABLE = "posts"
POSTS_FALLBACK_FILE = "post_pool.json"

# ==========================================
# ПОЛУЧЕНИЕ ПОСТОВ
# ==========================================
def get_posts(limit=50, status="draft"):
    """
    Возвращает список постов.
    Сначала пытается взять из Supabase, при ошибке — из post_pool.json.
    """
    # Попытка из базы
    filter_by = {"status": status} if status else None
    result = db_select(POSTS_TABLE, limit=limit, fallback_file=None, filter_by=filter_by)
    if result:
        return result
    
    # Фоллбэк на файл
    if os.path.exists(POSTS_FALLBACK_FILE):
        with open(POSTS_FALLBACK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [item for item in data if item.get("status") == status][-limit:]
    return []

# ==========================================
# ДОБАВЛЕНИЕ ПОСТА
# ==========================================
def add_post(text, tags=None, author_id=None):
    """
    Добавляет пост в пул.
    Сначала пытается записать в Supabase, при ошибке — в post_pool.json.
    """
    data = {
        "text": text,
        "tags": tags or [],
        "author_id": author_id,
        "status": "draft",
        "created_at": datetime.now().isoformat()
    }
    db_insert(POSTS_TABLE, data, fallback_file=POSTS_FALLBACK_FILE)
    return True

# ==========================================
# УДАЛЕНИЕ ПОСТА
# ==========================================
def delete_post(post_id):
    """
    Удаляет пост из пула.
    Сначала пытается удалить из Supabase, при ошибке — из post_pool.json.
    """
    client = get_client()
    if client:
        try:
            client.table(POSTS_TABLE).delete().eq("id", post_id).execute()
            debug_log("POSTS", f"Пост {post_id} удалён из базы", "INFO")
            return True
        except Exception as e:
            debug_log("POSTS", f"Ошибка удаления из базы: {e}", "ERROR")
    
    # Фоллбэк на файл
    if os.path.exists(POSTS_FALLBACK_FILE):
        with open(POSTS_FALLBACK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        new_data = [item for item in data if item.get("id") != post_id]
        with open(POSTS_FALLBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2)
        debug_log("POSTS", f"Пост {post_id} удалён из файла", "INFO")
    return True
