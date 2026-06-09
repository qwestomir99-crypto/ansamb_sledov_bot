# ==========================================
# Файл: bot/core.py
# Справка: README.md → Бот / Ядро
# Задача: глобальные обработчики, конфиг, токены
# Комментарий: исправлен умный поиск config.json с диагностикой
# ==========================================

import sys
import threading
import traceback
from datetime import datetime
import os
import json
import telebot

ERROR_LOG = "error.log"

def global_exception_handler(exc_type, exc_value, exc_traceback):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tb_lines = traceback.format_tb(exc_traceback)
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {exc_type.__name__}: {exc_value}\n")
        f.write(''.join(tb_lines))
        f.write("\n" + "-"*50 + "\n")
    print(f"[EXCEPTION] {exc_type.__name__}: {exc_value}")

def thread_exception_handler(args):
    global_exception_handler(args.exc_type, args.exc_value, args.exc_traceback)

sys.excepthook = global_exception_handler
threading.excepthook = thread_exception_handler

def load_config():
    """Умная загрузка config.json с диагностикой путей"""
    import os
    import json
    
    # Вариант 1: прямой абсолютный путь (Bothost)
    path1 = '/app/dialogue/data/config.json'
    # Вариант 2: относительный через __file__
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    path2 = os.path.join(project_root, 'dialogue', 'data', 'config.json')
    # Вариант 3: без начального слеша (для экспериментов)
    path3 = 'dialogue/data/config.json'
    
    print("=== ДИАГНОСТИКА load_config ===")
    print(f"Вариант 1 (абсолютный): {path1}")
    print(f"  существует? {os.path.exists(path1)}")
    print(f"Вариант 2 (через __file__): {path2}")
    print(f"  существует? {os.path.exists(path2)}")
    print(f"Вариант 3 (относительный): {path3}")
    print(f"  существует? {os.path.exists(path3)}")
    print("================================")
    
    # Пробуем открыть первый существующий
    for path in [path1, path2, path3]:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"✅ config.json загружен из: {path}")
                    return config
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка в JSON: {e}")
                raise ValueError(f"Ошибка в формате config.json ({path}): {e}")
    
    # Если ни один не подошёл
    raise FileNotFoundError(
        f"❌ Не найден config.json!\n"
        f"Проверенные пути:\n"
        f"  - {path1}\n"
        f"  - {path2}\n"
        f"  - {path3}"
    )

def get_bot():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN не задан")
    return telebot.TeleBot(TOKEN)

def get_admin_user_id():
    return int(os.environ.get("ADMIN_USER_ID", 0))

def get_vk_token():
    return os.environ.get("VK_TOKEN")

def get_vk_owner_id():
    return os.environ.get("VK_OWNER_ID")

def get_vk_reader_token():
    """Короткий сервисный ключ группы (71 символ) — для VK Reader"""
    return os.environ.get("VK_READER_TOKEN")

def get_vk_group_id():
    """ID сообщества VK — для публикации в группу"""
    return os.environ.get("VK_GROUP_ID")
