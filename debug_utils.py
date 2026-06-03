# ==========================================
# Файл: debug_utils.py
# Справка: README.md → Отладка / Дебаггер
# Задача: единая система логирования для всех модулей
# Комментарий: ТОЛЬКО ЯДРО (без отправки в Telegram)
# Зависит от: logging, os, datetime, traceback, json
# Вызывается из: bot.py, app.py, agent.py, services/*.py, dialogue/*.py
# ==========================================

import os
import json
import logging
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

# ==========================================
# 1. ПОДАВЛЕНИЕ ШУМА
# ==========================================
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

# ==========================================
# 2. НАСТРОЙКА ЛОГГЕРА
# ==========================================

debug_logger = logging.getLogger("AnsamblDebug")
debug_logger.setLevel(logging.DEBUG)

if debug_logger.hasHandlers():
    debug_logger.handlers.clear()

# ==========================================
# 3. КОНСОЛЬНЫЙ ВЫВОД (цветной)
# ==========================================
try:
    import colorlog
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s[%(levelname)s] %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white'
        }
    ))
except ImportError:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
debug_logger.addHandler(console_handler)

# ==========================================
# 4. ФАЙЛОВЫЙ ЛОГ
# ==========================================
log_file = "debug.log"
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=1024 * 1024,  # 1 МБ
    backupCount=1,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
debug_logger.addHandler(file_handler)

# ==========================================
# 5. ОСНОВНЫЕ ФУНКЦИИ
# ==========================================
def debug_log(module, message, level="INFO"):
    log_func = getattr(debug_logger, level.lower(), debug_logger.info)
    log_func(f"[{module}] {message}")

def log_exception(module, e):
    tb = traceback.format_exc()
    debug_logger.error(f"[{module}] Исключение: {type(e).__name__}: {e}\n{tb}")

# ==========================================
# 6. ПОЛУЧЕНИЕ ЛОГОВ ДЛЯ ОТЧЁТОВ
# ==========================================
def get_logs(limit=100):
    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return ''.join(lines[-limit:]) if lines else "Лог-файл пуст"
        else:
            return "Лог-файл не найден"
    except Exception as e:
        return f"Ошибка чтения логов: {e}"

def get_logs_as_dict(limit=100):
    try:
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        
        logs = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(" | ", 3)
            if len(parts) >= 4:
                logs.append({
                    "timestamp": parts[0],
                    "level": parts[1],
                    "module": parts[2],
                    "message": parts[3]
                })
            else:
                logs.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "level": "INFO",
                    "module": "unknown",
                    "message": line
                })
        return logs
    except Exception as e:
        return [{"level": "ERROR", "message": f"Ошибка парсинга логов: {e}"}]

# ==========================================
# 7. ОТПРАВКА ОТЧЁТОВ В TELEGRAM (вызывается из debug.py)
# ==========================================
def send_debug_report(bot, chat_id, limit=100):
    logs = get_logs(limit)
    if not logs or logs == "Лог-файл не найден" or logs == "Лог-файл пуст":
        bot.send_message(chat_id, "📭 Лог-файл пуст или не найден.")
        return
    
    max_len = 4000
    if len(logs) <= max_len:
        bot.send_message(chat_id, f"```\n{logs}\n```", parse_mode='Markdown')
    else:
        for i in range(0, len(logs), max_len):
            part = logs[i:i+max_len]
            bot.send_message(chat_id, f"```\n{part}\n```", parse_mode='Markdown')

# ==========================================
# 8. АУДИТ (вызывается из debug_audit.py)
# ==========================================
def run_audit():
    try:
        from debug_audit import run_audit as audit
        return audit()
    except ImportError:
        debug_log("DEBUG", "debug_audit.py не найден, аудит недоступен", "WARNING")
        return None
    except Exception as e:
        log_exception("DEBUG", e)
        return None

def get_audit_status():
    index_file = "debug_index.json"
    if not os.path.exists(index_file):
        return {"audit_exists": False}
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "audit_exists": True,
                "last_audit": data.get("last_audit", "никогда"),
                "results": data.get("audit_results", {})
            }
    except Exception as e:
        return {"audit_exists": False, "error": str(e)}

# ==========================================
# 9. ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ ДЕБАГГЕРА ===\n")
    debug_log("TEST", "Дебаггер загружен", "INFO")
    debug_log("TEST", "Тестовое сообщение", "DEBUG")
    debug_log("TEST", "Тестовое предупреждение", "WARNING")
    debug_log("TEST", "Тестовая ошибка", "ERROR")
    
    print("\n=== Последние 10 строк лога ===")
    print(get_logs(10))
    
    print("\n=== Статус аудита ===")
    print(get_audit_status())
