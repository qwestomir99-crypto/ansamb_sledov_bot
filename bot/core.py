#!/usr/bin/env python3
# ==========================================
# Файл: bot/core.py
# Справка: README.md → Бот / Ядро
# Задача: глобальные обработчики, конфиг, токены
# ==========================================

import sys
import os
import json
import telebot
import threading
import traceback
from datetime import datetime
from services.secrets_manager import get_secret

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
    """Загружает config.json: сначала /app/shared/, потом PostgreSQL, потом файлы"""
    
    # Определяем корень проекта
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # === Попытка 1: Общая папка (для совместимости) ===
    shared_path = os.path.join(project_root, 'shared', 'config.json')
    if os.path.exists(shared_path):
        try:
            with open(shared_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"✅ config.json загружен из {shared_path}")
                return config
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка JSON в {shared_path}: {e}")
    
    # === Попытка 2: PostgreSQL ===
    try:
        from services.sqlite_client import load_config_from_db
        config = load_config_from_db()
        if config:
            print("✅ config.json загружен из PostgreSQL")
            return config
    except Exception as e:
        print(f"[CONFIG] PostgreSQL недоступен: {e}")
    
    # === Попытка 3: Локальные файлы ===
    possible_paths = [
        os.path.join(project_root, 'dialogue', 'data', 'config.json'),
        'dialogue/data/config.json'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"✅ config.json загружен из {path}")
                    return config
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка JSON ({path}): {e}")
                raise ValueError(f"Ошибка в формате config.json ({path}): {e}")
    
    raise FileNotFoundError(
        f"❌ Не найден config.json!\n"
        f"Проверенные пути:\n"
        f"  - {shared_path}\n"
        f"  - PostgreSQL\n"
        f"  - {possible_paths[0]}\n"
        f"  - {possible_paths[1]}"
    )

def get_bot():
    TOKEN = get_secret("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN не задан")
    return telebot.TeleBot(TOKEN)

def get_admin_user_id():
    uid = get_secret("ADMIN_USER_ID")
    return int(uid) if uid else 0

def get_vk_token():
    return get_secret("VK_TOKEN")

def get_vk_owner_id():
    value = get_secret("VK_OWNER_ID")
    try:
        return int(value) if value else 0
    except:
        return 0

def get_vk_reader_token():
    return get_secret("VK_READER_TOKEN")

def get_vk_group_id():
    return get_secret("VK_GROUP_ID")
