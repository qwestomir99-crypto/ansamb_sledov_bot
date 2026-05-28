# ==========================================
# Файл: services/sql_analytics.py
# Справка: README.md → Аналитика / SQL
# Задача: сбор аналитики напрямую в Supabase
# Комментарий: вытесняет файловую аналитику, но сохраняет фоллбэк
# Зависит от: services.supabase_client, datetime, debug_utils
# Вызывается из: bot.py (при старте), web_api/analytics.py
# ==========================================

from datetime import datetime
from services.supabase_client import db_insert, db_select
from debug_utils import debug_log

ANALYTICS_TABLE = "analytics"

def log_sql(level, message):
    debug_log("SQL_ANALYTICS", message, level)

def record_activity(module, action, metadata=None):
    """Записывает активность в SQL"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "action": action,
        "metadata": metadata or {}
    }
    db_insert(ANALYTICS_TABLE, data)
    log_sql("INFO", f"Активность записана: {module}.{action}")

def get_activity_by_hour(hours=24):
    """Возвращает активность по часам (из SQL)"""
    result = db_select(
        ANALYTICS_TABLE,
        limit=1000,
        filter_by={"module": "web"}
    )
    # Группировка по часам (упрощённо)
    hourly = {}
    for row in result:
        hour = row["timestamp"][:13]  # 2026-05-28T15
        hourly[hour] = hourly.get(hour, 0) + 1
    return sorted(hourly.items())

def get_top_errors(limit=5):
    """Возвращает топ ошибок (из SQL)"""
    result = db_select(
        ANALYTICS_TABLE,
        limit=500,
        filter_by={"level": "ERROR"}
    )
    errors = {}
    for row in result:
        module = row.get("module")
        errors[module] = errors.get(module, 0) + 1
    return sorted(errors.items(), key=lambda x: x[1], reverse=True)[:limit]
