# ==========================================
# Файл: web_app.py
# Справка: README.md → Веб-морда / Точка входа для Bothost
# Задача: запуск Flask как основного процесса, бот — в фоне
# Комментарий: чтобы Bothost увидел HTTP-сервер и не добавлял обёртку
# ==========================================

import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.app import app
from ping_utils import start_background_pinger, start_agent_pinger

if __name__ == "__main__":
    # Пингеры в фоне
    try:
        start_background_pinger(interval=60)
        start_agent_pinger()
        print("[WEB] Пингеры запущены")
    except Exception as e:
        print(f"[WEB] Ошибка пингеров: {e}")
    
    # Telegram-бот в фоновом потоке
    def start_tg_bot():
        from bot.main import main
        main()
    
    threading.Thread(target=start_tg_bot, daemon=True).start()
    print("[WEB] Telegram-бот запущен в фоне")
    
    # Flask — основной процесс
    port = int(os.environ.get("PORT", 10000))
    print(f"[WEB] Веб-морда на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
