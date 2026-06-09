#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import threading

# ==========================================
# ДИАГНОСТИКА: поиск старого config.json
# ==========================================
print("=== ПОИСК ФАЙЛОВ С config.json ===")
for root, dirs, files in os.walk('.'):
    # Игнорируем виртуальное окружение и скрытые папки
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
                        # Ищем строки с config.json, но не из уже исправленных модулей
                        if 'config.json' in line and 'load_app_config' not in line:
                            print(f"  {path}:{i} - {line.strip()[:80]}")
            except Exception as e:
                print(f"  Ошибка чтения {path}: {e}")
print("=== КОНЕЦ ПОИСКА ===")
# ==========================================

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.app import app
from ping_utils import start_background_pinger, start_agent_pinger

if __name__ == "__main__":
    # Запускаем пингеры
    try:
        start_background_pinger(interval=60)
        start_agent_pinger()
        print("[BOT] Пингеры запущены")
    except Exception as e:
        print(f"[BOT] Ошибка запуска пингеров: {e}")
    
    # Веб-морда в фоне
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=app.run, args=('0.0.0.0', port), daemon=True).start()
    
    # Бот в основном потоке
    from bot.main import main
    main()
