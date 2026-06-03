# ==========================================
# Файл: services/analytics_fallback.py
# Справка: README.md → Аналитика / Фоллбэк
# Задача: фоллбэк на файлы для аналитики
# Комментарий: сохраняет ядро, если SQL недоступен
# Зависит от: os, json, datetime, debug_utils
# Вызывается из: sql_analytics.py (при ошибке)
# ==========================================

import os
import json
from datetime import datetime
from debug_utils import debug_log

ANALYTICS_FALLBACK_FILE = "analytics.json"

def log_fb(level, message):
    debug_log("ANALYTICS_FALLBACK", message, level)

def load_fallback():
    if not os.path.exists(ANALYTICS_FALLBACK_FILE):
        return {"activity": [], "errors": []}
    with open(ANALYTICS_FALLBACK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_fallback(data):
    with open(ANALYTICS_FALLBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def record_activity_fallback(module, action, metadata=None):
    data = load_fallback()
    data["activity"].append({
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "action": action,
        "metadata": metadata or {}
    })
    if len(data["activity"]) > 1000:
        data["activity"] = data["activity"][-1000:]
    save_fallback(data)
    log_fb("INFO", f"Активность записана в файл: {module}.{action}")

def get_activity_by_hour_fallback(hours=24):
    data = load_fallback()
    # Группировка по часам (упрощённо)
    hourly = {}
    for row in data["activity"]:
        if "timestamp" in row:
            hour = row["timestamp"][:13]
            hourly[hour] = hourly.get(hour, 0) + 1
    return sorted(hourly.items())
