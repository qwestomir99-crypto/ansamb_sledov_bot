# ==========================================
# Файл: services/dialogue/exception_handler.py
# Справка: README.md → Обработка исключений
# Задача: перехват и логирование ошибок в сервисах
# Комментарий: используется для отлова ошибок в autoposter, photo_reader и др.
# Зависит от: traceback, datetime
# Вызывается из: services/autoposter.py, services/photo_reader.py
# ==========================================

import traceback
from datetime import datetime

def log_exception(service_name, e, log_file="error.log"):
    """
    Логирует исключение в файл и в консоль.
    
    Args:
        service_name: имя сервиса (например "AUTOPOSTER")
        e: объект исключения
        log_file: путь к файлу лога (по умолчанию error.log)
    """
    error_msg = f"{datetime.now()} | [{service_name}] {type(e).__name__}: {e}\n"
    error_msg += traceback.format_exc()
    error_msg += "\n" + "-" * 50 + "\n"
    
    print(error_msg)
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(error_msg)
    except:
        pass

def safe_execute(service_name, func, *args, **kwargs):
    """
    Безопасно выполняет функцию, перехватывая и логируя ошибки.
    
    Returns:
        результат функции или None при ошибке
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log_exception(service_name, e)
        return None
