# ==========================================
# Файл: services/sql_analytics.py
# Справка: README.md → Аналитика / PostgreSQL
# Задача: сбор аналитики напрямую в PostgreSQL с автоматической очисткой
# Комментарий: переход с SQLite на PostgreSQL
# Зависит от: datetime, debug_utils, psycopg2
# Вызывается из: bot.py, web_api/analytics.py, routing_engine.py
# ==========================================

import os
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from debug_utils import debug_log

DATABASE_URL = os.environ.get("DATABASE_URL")

def log_sql(level, message):
    debug_log("SQL_ANALYTICS", message, level)

def get_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL не задан")
    return psycopg2.connect(DATABASE_URL)

def init_analytics_db():
    """Создаёт таблицу analytics, если её нет"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id SERIAL PRIMARY KEY,
                timestamp TEXT,
                module TEXT,
                action TEXT,
                status TEXT,
                metadata TEXT
            )
        ''')
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp);
        ''')
        conn.commit()
        conn.close()
        log_sql("INFO", "Таблица analytics создана/подтверждена")
    except Exception as e:
        log_sql("ERROR", f"Ошибка инициализации БД: {e}")

def record_activity(module, action, metadata=None, status="info"):
    """Записывает активность в PostgreSQL"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "action": action,
        "status": status,
        "metadata": metadata or {}
    }
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO analytics (timestamp, module, action, status, metadata) VALUES (%s, %s, %s, %s, %s)",
            (data["timestamp"], data["module"], data["action"], data["status"], str(data["metadata"]))
        )
        conn.commit()
        conn.close()
        log_sql("INFO", f"Активность записана: {module}.{action} ({status})")
    except Exception as e:
        log_sql("ERROR", f"Ошибка записи: {e}")

def clean_old_analytics(days=7):
    """Удаляет записи старше days дней"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM analytics WHERE timestamp < NOW() - INTERVAL '%s days'", (days,))
        conn.commit()
        conn.close()
        log_sql("INFO", f"Очищена аналитика старше {days} дней")
    except Exception as e:
        log_sql("ERROR", f"Ошибка очистки аналитики: {e}")

def get_routing_context():
    """Возвращает контекст для маршрутизации на основе аналитики"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM analytics WHERE module = %s AND timestamp > NOW() - INTERVAL '1 hour'", ("web",))
        activity_count = c.fetchone()[0]
        conn.close()
        
        if activity_count > 50:
            level = "high"
        elif activity_count > 10:
            level = "medium"
        else:
            level = "low"
        
        return {
            "activity": activity_count,
            "level": level,
            "last_update": datetime.now().isoformat()
        }
    except Exception as e:
        log_sql("ERROR", f"Ошибка получения контекста: {e}")
        return {"activity": 0, "level": "low", "last_update": datetime.now().isoformat()}

def get_detailed_routing_context():
    """Возвращает расширенный контекст для маршрутизации"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT module, status FROM analytics WHERE timestamp > NOW() - INTERVAL '1 hour'")
        rows = c.fetchall()
        conn.close()
        
        errors = {}
        success_count = 0
        total = len(rows)
        
        for module, status in rows:
            if status == "error":
                errors[module] = errors.get(module, 0) + 1
            if status == "success":
                success_count += 1
        
        return {
            "activity": total,
            "error_rate": len(errors) / max(total, 1),
            "success_rate": success_count / max(total, 1),
            "top_errors": sorted(errors.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    except Exception as e:
        log_sql("ERROR", f"Ошибка получения контекста: {e}")
        return {"activity": 0, "error_rate": 0, "success_rate": 0, "top_errors": []}

def get_activity_by_hour(hours=24):
    """Возвращает активность по часам"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT timestamp FROM analytics WHERE module = %s AND timestamp > NOW() - INTERVAL '%s hours'", ("web", hours))
        rows = c.fetchall()
        conn.close()
        
        hourly = {}
        for row in rows:
            hour = row[0][:13]
            hourly[hour] = hourly.get(hour, 0) + 1
        return sorted(hourly.items())
    except Exception as e:
        log_sql("ERROR", f"Ошибка получения активности: {e}")
        return []

def get_top_errors(limit=5):
    """Возвращает топ ошибок"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT module, COUNT(*) FROM analytics WHERE status = %s GROUP BY module ORDER BY COUNT(*) DESC LIMIT %s", ("error", limit))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        log_sql("ERROR", f"Ошибка получения топ ошибок: {e}")
        return []

# Инициализация при импорте
init_analytics_db()
