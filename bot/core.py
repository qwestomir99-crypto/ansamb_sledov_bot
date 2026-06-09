# ==========================================
# Файл: bot/core.py
# Справка: README.md → Бот / Ядро
# Задача: глобальные обработчики, конфиг, токены
# Комментарий: config.json ищется автоматически относительно bot.py
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
    """
    Загружает config.json из папки dialogue/data.
    Ищет файл относительно расположения этого скрипта (bot/core.py),
    а не относительно текущей рабочей директории.
    """
    # Получаем абсолютный путь к каталогу, где находится этот файл (bot/core.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Поднимаемся на один уровень вверх, чтобы попасть в корень проекта (папку с bot.py)
    project_root = os.path.dirname(current_dir)
    # Формируем полный путь к config.json
    config_path = os.path.join(project_root, 'dialogue', 'data', 'config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ Не найден config.json по пути: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ Ошибка в формате config.json: {e}")

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
