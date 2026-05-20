# ==========================================
# Файл: debug_utils.py
# Справка: README.md → Дебаггер
# Задача: централизованный дебаг-логгер
# Комментарий: включается/выключается одной переменной. Ошибки выводятся всегда.
# Зависит от: settings.py
# Вызывается из: любого модуля
# ==========================================

import sys
from datetime import datetime

# Пытаемся загрузить настройки, если не получилось — используем значения по умолчанию
try:
    from settings import DEBUG_MODE, DEBUG_MODULES
except ImportError:
    DEBUG_MODE = True
    DEBUG_MODULES = []

def debug_log(module, message, level="INFO"):
    """
    Условный вывод лога.
    - Если DEBUG_MODE = False — ничего не выводит (кроме ошибок, если level="ERROR").
    - Если DEBUG_MODULES не пустой — выводит только для указанных модулей.
    """
    if not DEBUG_MODE and level != "ERROR":
        return
    if DEBUG_MODULES and module not in DEBUG_MODULES and level != "ERROR":
        return
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{module}] {level}: {message}")

def log_error(module, error):
    """Ошибки всегда выводятся, без проверки DEBUG_MODE"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{module}] ❌ ОШИБКА: {error}")
