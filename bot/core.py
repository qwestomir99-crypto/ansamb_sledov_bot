# ==========================================
# Файл: bot/core.py
# Справка: README.md → Бот / Ядро
# Задача: глобальные обработчики, конфиг, токены
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

# Путь к файлу конфигурации
CONFIG_FILE = os.path.join('dialogue', 'data', 'config.json')

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

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
