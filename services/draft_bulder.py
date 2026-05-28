# ==========================================
# Файл: services/draft_builder.py
# Справка: README.md → Сборщик черновиков
# Задача: создание и хранение черновиков постов
# Комментарий: используется Алисой для сборки постов
# Зависит от: json, os, datetime, debug_utils
# Вызывается из: Alice/post_builder.py
# ==========================================

import os
import json
from datetime import datetime
from debug_utils import debug_log

DRAFTS_FILE = "data/drafts.json"

def log_db(level, message):
    debug_log("DRAFT_BUILDER", message, level)

def load_drafts():
    if not os.path.exists(DRAFTS_FILE):
        return []
    with open(DRAFTS_FILE, "r") as f:
        return json.load(f)

def save_drafts(drafts):
    with open(DRAFTS_FILE, "w") as f:
        json.dump(drafts, f, indent=2)

def create_draft(title, content, media=None, tags=None):
    drafts = load_drafts()
    draft = {
        "id": len(drafts) + 1,
        "title": title,
        "content": content,
        "media": media or [],
        "tags": tags or [],
        "created_at": datetime.now().isoformat(),
        "status": "draft"
    }
    drafts.append(draft)
    save_drafts(drafts)
    log_db("INFO", f"Создан черновик: {title}")
    return draft

def get_draft(draft_id):
    drafts = load_drafts()
    for d in drafts:
        if d["id"] == draft_id:
            return d
    return None

def update_draft(draft_id, **kwargs):
    drafts = load_drafts()
    for d in drafts:
        if d["id"] == draft_id:
            for key, value in kwargs.items():
                d[key] = value
            save_drafts(drafts)
            log_db("INFO", f"Черновик {draft_id} обновлён")
            return True
    return False

def delete_draft(draft_id):
    drafts = load_drafts()
    drafts = [d for d in drafts if d["id"] != draft_id]
    save_drafts(drafts)
    log_db("INFO", f"Черновик {draft_id} удалён")
    return True

def list_drafts():
    return load_drafts()
