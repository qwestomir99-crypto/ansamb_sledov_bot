#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import threading

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.app import app
from ping_utils import start_background_pinger, start_agent_pinger

if __name__ == "__main__":
    # Запускаем пингеры в фоне
    try:
        start_background_pinger(interval=60)
        start_agent_pinger()
        print("[BOT] Пингеры запущены")
    except Exception as e:
        print(f"[BOT] Ошибка запуска пингеров: {e}")
    
    # Telegram-бот в фоновом потоке
    def start_tg_bot():
        from bot.main import main
        main()
    
    threading.Thread(target=start_tg_bot, daemon=True).start()
    print("[BOT] Telegram-бот запущен в фоне")
    
    # Веб-морда — основной процесс (для Bothost)
    port = int(os.environ.get("PORT", 10000))
    print(f"[WEB] Запуск веб-морды на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
