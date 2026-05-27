# ==========================================
# Файл: services/log_cleaner.py
# Справка: README.md → Веб-морда / Очистка логов
# Задача: очистка и ротация логов
# Комментарий: вынесено из bot.py
# Зависит от: os, time, debug_utils
# Вызывается из: bot.py (запуск потока)
# ==========================================

import os
import time
import threading
from debug_utils import debug_log

def clean_old_logs(days=7, max_size_mb=1):
    now = time.time()
    max_size_bytes = max_size_mb * 1024 * 1024
    for logfile in ['admin.log', 'error.log', 'debug.log']:
        if not os.path.exists(logfile):
            continue
        mtime = os.path.getmtime(logfile)
        if now - mtime > days * 86400:
            os.remove(logfile)
            with open(logfile, 'w') as f:
                f.write('')
            debug_log("LOG_CLEANER", f"{logfile} удалён (старше {days} дней)", "INFO")
            continue
        if os.path.getsize(logfile) > max_size_bytes:
            with open(logfile, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            lines_to_keep = lines[-500:] if len(lines) > 500 else lines
            with open(logfile, 'w', encoding='utf-8') as f:
                f.writelines(lines_to_keep)
            debug_log("LOG_CLEANER", f"{logfile} обрезан (был >{max_size_mb} МБ)", "INFO")

def start_log_cleaner():
    def cleaner_loop():
        clean_old_logs()
        while True:
            time.sleep(86400)
            clean_old_logs()
    threading.Thread(target=cleaner_loop, daemon=True).start()
    debug_log("LOG_CLEANER", "Очистка логов запущена", "INFO")
