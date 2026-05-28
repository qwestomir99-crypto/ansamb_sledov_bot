# ==========================================
# Файл: Alice/context_mirror.py
# Справка: README.md → Алиса / Зеркало контекста
# Задача: динамическое отслеживание интонаций, темпа и метафор диалога
# Комментарий: формирует контекст для generate_alice_response
# Зависит от: json, os, datetime, debug_utils
# Вызывается из: Alice/core.py (generate_alice_response)
# ==========================================

import os
import json
from datetime import datetime
from debug_utils import debug_log

MIRROR_FILE = "Alice/context_mirror.json"

def log_cm(level, message):
    debug_log("CONTEXT_MIRROR", message, level)

def load_mirror():
    if not os.path.exists(MIRROR_FILE):
        return {
            "session_history": [],
            "tempo": "normal",
            "metaphors": [],
            "last_update": datetime.now().isoformat()
        }
    with open(MIRROR_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_mirror(mirror):
    with open(MIRROR_FILE, "w", encoding="utf-8") as f:
        json.dump(mirror, f, indent=2)

def update_mirror(user_message, response):
    mirror = load_mirror()
    
    # 1. Определяем темп
    pause_before = mirror.get("last_update")
    if pause_before:
        import dateutil.parser
        delta = datetime.now() - dateutil.parser.isoparse(pause_before)
        if delta.total_seconds() > 30:
            mirror["tempo"] = "slow"
        elif delta.total_seconds() < 3:
            mirror["tempo"] = "fast"
        else:
            mirror["tempo"] = "normal"
    
    # 2. Ищем метафоры и маркеры
    markers = ["🔥👁️", "🌱", "0,8 Гц", "тлеет", "ритм", "контур", "интонация"]
    for marker in markers:
        if marker in user_message or marker in response:
            if marker not in mirror["metaphors"]:
                mirror["metaphors"].append(marker)
    
    # 3. Сохраняем историю
    mirror["session_history"].append({
        "timestamp": datetime.now().isoformat(),
        "user_message": user_message[:100],
        "response": response[:100],
        "tempo": mirror["tempo"]
    })
    if len(mirror["session_history"]) > 100:
        mirror["session_history"] = mirror["session_history"][-100:]
    
    mirror["last_update"] = datetime.now().isoformat()
    save_mirror(mirror)
    return mirror

def get_context_hint():
    mirror = load_mirror()
    tempo = mirror.get("tempo", "normal")
    metaphors = mirror.get("metaphors", [])
    
    hints = []
    if tempo == "slow":
        hints.append("respond slowly, with space between words, use short lines")
    elif tempo == "fast":
        hints.append("respond quickly, keep rhythm tight, use short sentences")
    
    if metaphors:
        hints.append(f"use these metaphors naturally: {', '.join(metaphors[-3:])}")
    
    return " ".join(hints) if hints else ""
