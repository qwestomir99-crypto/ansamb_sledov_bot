# ==========================================
# Файл: services/sql_analytics.py
# Справка: README.md → Аналитика / SQL
# Задача: сбор аналитики напрямую в SQLite
# Комментарий: теперь на SQLite (а не на Supabase), фоллбэк не нужен
# Зависит от: datetime, debug_utils, sqlite3
# Вызывается из: bot.py, web_api/analytics.py, routing_engine.py
# ==========================================

import sqlite3
import os
from datetime import datetime
from debug_utils import debug_log

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'analytics.db')

def log_sql(level, message):
    debug_log("SQL_ANALYTICS", message, level)

def init_analytics_db():
    """Создаёт таблицу analytics, если её нет"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                module TEXT,
                action TEXT,
                status TEXT,
                metadata TEXT
            )
        ''')
        conn.commit()
        conn.close()
        log_sql("INFO", "Таблица analytics создана/подтверждена")
    except Exception as e:
        log_sql("ERROR", f"Ошибка инициализации БД: {e}")

def record_activity(module, action, metadata=None, status="info"):
    """Записывает активность в SQLite"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "action": action,
        "status": status,
        "metadata": metadata or {}
    }
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO analytics (timestamp, module, action, status, metadata) VALUES (?, ?, ?, ?, ?)",
            (data["timestamp"], data["module"], data["action"], data["status"], str(data["metadata"]))
        )
        conn.commit()
        conn.close()
        log_sql("INFO", f"Активность записана: {module}.{action} ({status})")
    except Exception as e:
        log_sql("ERROR", f"Ошибка записи: {e}")

def get_routing_context():
    """Возвращает контекст для маршрутизации на основе аналитики"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM analytics WHERE module = ? AND datetime(timestamp) > datetime('now', '-1 hour')", ("web",))
        activity_count = c.fetchone()[0]
        conn.close()
        
        # Определяем уровень активности
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
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT module, status FROM analytics WHERE datetime(timestamp) > datetime('now', '-1 hour')")
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
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT timestamp FROM analytics WHERE module = ? AND datetime(timestamp) > datetime('now', '-? hour')", ("web", hours))
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
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT module, COUNT(*) FROM analytics WHERE status = ? GROUP BY module ORDER BY COUNT(*) DESC LIMIT ?", ("error", limit))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        log_sql("ERROR", f"Ошибка получения топ ошибок: {e}")
        return []

# Инициализация при импорте
init_analytics_db()
