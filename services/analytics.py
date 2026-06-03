# ==========================================
# Файл: services/analytics.py
# Справка: README.md → Аналитика
# Задача: сбор и отображение аналитики через SQLite
# Комментарий: полностью переписан под локальную SQLite
# ==========================================

from datetime import datetime, timedelta
from debug_utils import debug_log
from services.sqlite_client import get_messages

def log_analytics(level, message):
    debug_log("ANALYTICS", message, level)

def get_activity_by_hour(hours=24):
    """
    Возвращает активность по часам за последние N часов (из SQLite)
    """
    messages = get_messages(limit=2000)
    
    cutoff = datetime.now() - timedelta(hours=hours)
    hourly = {}
    
    for msg in messages:
        try:
            dt = datetime.fromisoformat(msg.get("timestamp"))
            if dt > cutoff:
                hour = dt.strftime("%Y-%m-%d %H:00")
                hourly[hour] = hourly.get(hour, 0) + 1
        except:
            continue
    
    sorted_hours = sorted(hourly.items(), key=lambda x: x[0])
    return sorted_hours

def get_top_errors(limit=5):
    """
    Возвращает топ ошибок (из логов)
    """
    errors = {}
    log_file = "debug.log"
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if "ERROR" in line:
                    parts = line.split("|")
                    module = parts[2].strip() if len(parts) > 2 else "unknown"
                    errors[module] = errors.get(module, 0) + 1
    except Exception as e:
        log_analytics("ERROR", f"Ошибка чтения логов: {e}")
    
    top = sorted(errors.items(), key=lambda x: x[1], reverse=True)[:limit]
    return top

def get_activity_summary():
    """
    Возвращает сводку активности за последние 24 часа
    """
    messages = get_messages(limit=2000)
    now = datetime.now()
    day_ago = now - timedelta(days=1)
    
    total = 0
    for msg in messages:
        try:
            dt = datetime.fromisoformat(msg.get("timestamp"))
            if dt > day_ago:
                total += 1
        except:
            continue
    
    # Получаем топ модулей из сообщений
    module_counts = {}
    for msg in messages:
        source = msg.get("source", "unknown")
        module_counts[source] = module_counts.get(source, 0) + 1
    
    top_module = max(module_counts.items(), key=lambda x: x[1])[0] if module_counts else "unknown"
    
    return {
        "last_24h": total,
        "unique_modules": len(module_counts),
        "top_module": top_module
    }
