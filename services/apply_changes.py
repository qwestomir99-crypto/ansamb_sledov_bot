# ==========================================
# Файл: services/apply_changes.py
# Справка: README.md → Алиса / Применение изменений
# Задача: безопасное применение изменений к файлам
# Комментарий: вызывается из suggestion_engine.py после утверждения
# Зависит от: os, shutil, datetime, debug_utils
# Вызывается из: suggestion_engine.py (approve_suggestion)
# ==========================================

import os
import shutil
from datetime import datetime
from debug_utils import debug_log

def log_ac(level, message):
    debug_log("APPLY_CHANGES", message, level)

def apply_change(target_file, new_code, backup=True):
    """
    Применяет изменения к файлу.
    Если backup=True, создаёт резервную копию.
    """
    if not os.path.exists(target_file):
        log_ac("ERROR", f"Файл {target_file} не найден")
        return False
    
    # Создаём резервную копию
    if backup:
        backup_file = f"{target_file}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(target_file, backup_file)
        log_ac("INFO", f"Создана резервная копия: {backup_file}")
    
    # Записываем изменения
    try:
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_code)
        log_ac("INFO", f"Файл {target_file} обновлён")
        return True
    except Exception as e:
        log_ac("ERROR", f"Ошибка применения: {e}")
        return False
