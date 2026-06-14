#!/usr/bin/env python3
# ===========================================
# Файл: bot.py
# Справка: README.md - Бот / Точка входа
# Задача: запуск бота, веб-морды и пингеров
# ===========================================

import sys
import os

# ===== ПРАВИЛЬНЫЙ ПУТЬ К БИБЛИОТЕКАМ =====
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.local/lib/python3.10/site-packages'))
sys.path.insert(0, lib_path)
# ===========================================

# ===== ЗАГРУЗКА .ENV =====
from dotenv import load_dotenv
load_dotenv()
# ===========================================

import threading

print("=== ПОИСК ФАЙЛОВ С config.json ===")
for root, dirs, files in os.walk('.'):
    if '.venv' in dirs:
        dirs.remove('.venv')
    if 'env' in dirs:
        dirs.remove('env')
    if '__pycache__' in dirs:
        dirs.remove('__pycache__')
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        if 'config.json' in line and 'load_app_config' not in line:
                            print(f"  {path}:{i} - {line.strip()[:80]}")
            except Exception as e:
                print(f"  Ошибка чтения {path}: {e}")
print("=== КОНЕЦ ПОИСКА ===")

from services.app import app
from ping_utils import start_background_pinger, start_agent_pinger

if __name__ == "__main__":
    try:
        start_background_pinger(interval=60)
        start_agent_pinger()
        print("[BOT] Пингеры запущены")
    except Exception as e:
        print(f"[BOT] Ошибка запуска пингеров: {e}")

    port = int(os.getenv("PORT", 10000))
    threading.Thread(target=app.run, args=('0.0.0.0', port), daemon=True).start()

    from bot.main import main
    main()
