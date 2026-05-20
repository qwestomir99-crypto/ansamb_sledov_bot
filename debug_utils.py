# ==========================================
# Файл: debug_utils.py
# Справка: README.md → Дебаггер
# Задача: централизованный дебаг-логгер с ротацией и записью в файл
# Комментарий: пишет в консоль и в debug.log, управляется через settings.py
# Зависит от: settings.py
# Вызывается из: любого модуля
# ==========================================

import os
from datetime import datetime

# Пытаемся загрузить настройки, если не получилось — используем значения по умолчанию
try:
    from settings import DEBUG_MODE, DEBUG_MODULES
except ImportError:
    DEBUG_MODE = True
    DEBUG_MODULES = []

DEBUG_FILE = "debug.log"
MAX_DEBUG_SIZE = 1024 * 1024  # 1 МБ

def rotate_debug_log():
    """Если файл debug.log превышает лимит — удаляем старую половину"""
    if os.path.exists(DEBUG_FILE) and os.path.getsize(DEBUG_FILE) > MAX_DEBUG_SIZE:
        try:
            with open(DEBUG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            half = len(lines) // 2
            with open(DEBUG_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines[half:])
        except:
            pass

def write_debug_log(module, level, message):
    """Пишет дебаг-сообщение в файл"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(DEBUG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{module}] {level}: {message}\n")
        rotate_debug_log()
    except:
        pass

def debug_log(module, message, level="INFO"):
    """
    Условный вывод лога в консоль и файл.
    - Если DEBUG_MODE = False — ничего не выводит (кроме level="ERROR").
    - Если DEBUG_MODULES не пустой — выводит только для указанных модулей.
    """
    if not DEBUG_MODE and level != "ERROR":
        return
    if DEBUG_MODULES and module not in DEBUG_MODULES and level != "ERROR":
        return
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{module}] {level}: {message}")
    write_debug_log(module, level, message)

def log_error(module, error):
    """Ошибки всегда выводятся и пишутся в файл"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{module}] ❌ ОШИБКА: {error}")
    write_debug_log(module, "ERROR", error)
