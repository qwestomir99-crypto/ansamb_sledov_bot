# ==========================================
# Файл: services/analytics.py
# Справка: README.md → Аналитика
# Задача: сбор и отображение аналитики через Supabase
# Комментарий: использует таблицу logs из Supabase для метрик
# Зависит от: supabase_client, datetime, debug_utils
# Вызывается из: web_api.py (эндпоинты), admin.html (панель)
# ==========================================

import os
from datetime import datetime, timedelta
from debug_utils import debug_log
from services.supabase_client import db_select

# ==========================================
# КОНСТАНТЫ
# ==========================================
LOGS_TABLE = "logs"

def log_analytics(level, message):
    debug_log("ANALYTICS", message, level)

# ==========================================
# МЕТРИКИ
# ==========================================
def get_activity_by_hour(hours=24):
    """
    Возвращает активность по часам за последние N часов.
    """
    cutoff = datetime.now() - timedelta(hours=hours)
    result = db_select(
        LOGS_TABLE,
        limit=1000,
        filter_by={"level": "INFO"}
    )
    
    # Группируем по часам
    hourly = {}
    for row in result:
        try:
            dt = datetime.fromisoformat(row.get("timestamp"))
            hour = dt.strftime("%Y-%m-%d %H:00")
            hourly[hour] = hourly.get(hour, 0) + 1
        except:
            continue
    
    # Сортируем по времени
    sorted_hours = sorted(hourly.items(), key=lambda x: x[0])
    return sorted_hours

def get_top_errors(limit=5):
    """
    Возвращает топ ошибок по модулям.
    """
    result = db_select(
        LOGS_TABLE,
        limit=1000,
        filter_by={"level": "ERROR"}
    )
    
    # Группируем по модулям
    errors = {}
    for row in result:
        module = row.get("module")
        errors[module] = errors.get(module, 0) + 1
    
    # Сортируем и возвращаем топ
    top = sorted(errors.items(), key=lambda x: x[1], reverse=True)[:limit]
    return top

def get_activity_summary():
    """
    Возвращает сводку активности за последние 24 часа.
    """
    now = datetime.now()
    day_ago = now - timedelta(days=1)
    
    result = db_select(
        LOGS_TABLE,
        limit=1000,
        filter_by={"level": "INFO"}
    )
    
    total = 0
    for row in result:
        try:
            dt = datetime.fromisoformat(row.get("timestamp"))
            if dt > day_ago:
                total += 1
        except:
            continue
    
    return {
        "last_24h": total,
        "unique_modules": len(set(row.get("module") for row in result)),
        "top_module": "unknown"
    }
