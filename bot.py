# ==========================================
# Файл: bot.py
# Справка: README.md → Бот / Точка входа
# Задача: запуск бота, веб-морды и пингеров
# ==========================================

import os
import threading
from services.app import app
from ping_utils import start_background_pinger, start_agent_pinger

if __name__ == "__main__":
    # Запускаем пингеры (они сами уйдут в фоновые потоки)
    try:
        start_background_pinger(interval=60)  # пингует бота каждую минуту
        start_agent_pinger()                  # пингует агента
        print("[BOT] Пингеры запущены")
    except Exception as e:
        print(f"[BOT] Ошибка запуска пингеров: {e}")
    
    # Веб-морда в фоне
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=app.run, args=('0.0.0.0', port), daemon=True).start()
    
    # Бот в основном потоке — ошибки будут видны
    from bot.main import main
    main()
