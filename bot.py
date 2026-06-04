# ==========================================
# Файл: bot.py
# Справка: README.md → Бот / Точка входа
# Задача: запуск бота и веб-морды
# ==========================================

import os
import threading
from services.app import app

if __name__ == "__main__":
    # Веб-морда в фоне
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=app.run, args=('0.0.0.0', port), daemon=True).start()
    
    # Бот в основном потоке — ошибки будут видны
    from bot.main import main
    main()
