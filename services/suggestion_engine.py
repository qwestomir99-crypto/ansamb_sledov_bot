# ==========================================
# Файл: services/suggestion_engine.py
# Справка: README.md → Алиса / Инженер предложений
# Задача: управление предложениями Алисы по изменению кода
# Комментарий: Алиса пишет предложение, ты подтверждаешь — изменения применяются
# Зависит от: os, json, datetime, debug_utils
# Вызывается из: Alice/core.py, bot.py
# ==========================================

import os
import json
from datetime import datetime
from debug_utils import debug_log

SUGGESTIONS_FILE = "data/suggestions.json"

def log_se(level, message):
    debug_log("SUGGESTION_ENGINE", message, level)

def load_suggestions():
    if not os.path.exists(SUGGESTIONS_FILE):
        return {"pending": [], "applied": [], "rejected": []}
    with open(SUGGESTIONS_FILE, "r") as f:
        return json.load(f)

def save_suggestions(suggestions):
    with open(SUGGESTIONS_FILE, "w") as f:
        json.dump(suggestions, f, indent=2)

def create_suggestion(description, code_snippet, target_file):
    suggestions = load_suggestions()
    suggestion = {
        "id": len(suggestions["pending"]) + 1,
        "timestamp": datetime.now().isoformat(),
        "description": description,
        "code": code_snippet,
        "target_file": target_file,
        "status": "pending"
    }
    suggestions["pending"].append(suggestion)
    save_suggestions(suggestions)
    log_se("INFO", f"Создано предложение: {description}")
    return suggestion

def approve_suggestion(suggestion_id):
    suggestions = load_suggestions()
    for i, s in enumerate(suggestions["pending"]):
        if s["id"] == suggestion_id:
            s["status"] = "applied"
            suggestions["applied"].append(s)
            suggestions["pending"].pop(i)
            save_suggestions(suggestions)
            log_se("INFO", f"Предложение {suggestion_id} утверждено")
            # Применить изменения к файлу
            with open(s["target_file"], "w") as f:
                f.write(s["code"])
            return True
    return False

def reject_suggestion(suggestion_id):
    suggestions = load_suggestions()
    for i, s in enumerate(suggestions["pending"]):
        if s["id"] == suggestion_id:
            s["status"] = "rejected"
            suggestions["rejected"].append(s)
            suggestions["pending"].pop(i)
            save_suggestions(suggestions)
            log_se("INFO", f"Предложение {suggestion_id} отклонено")
            return True
    return False

def list_pending_suggestions():
    return load_suggestions()["pending"]
