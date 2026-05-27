# ==========================================
# Файл: services/exception_handler.py
# Справка: README.md → Веб-морда / Обработчик ошибок
# Задача: глобальный обработчик ошибок и потоков
# Комментарий: вынесено из bot.py
# Зависит от: sys, threading, datetime, debug_utils
# Вызывается из: bot.py (при старте)
# ==========================================

import sys
import threading
import traceback
from datetime import datetime
from debug_utils import debug_log

ERROR_LOG = "error.log"

def global_exception_handler(exc_type, exc_value, exc_traceback):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tb_lines = traceback.format_tb(exc_traceback)
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {exc_type.__name__}: {exc_value}\n")
        f.write(''.join(tb_lines))
        f.write("\n" + "-"*50 + "\n")
    debug_log("EXCEPTION", f"{exc_type.__name__}: {exc_value}", "ERROR")

def thread_exception_handler(args):
    global_exception_handler(args.exc_type, args.exc_value, args.exc_traceback)

def register_exception_handlers():
    sys.excepthook = global_exception_handler
    threading.excepthook = thread_exception_handler
    debug_log("EXCEPTION", "Глобальные обработчики ошибок зарегистрированы", "INFO")
