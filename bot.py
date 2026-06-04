# ==========================================
# Файл: bot.py
# Справка: README.md → Бот / Точка входа
# Задача: запуск бота и веб-морды
# ==========================================

import os
import threading
from services.app import app

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    from bot.main import main
    threading.Thread(target=main, daemon=True).start()
    
    # Запускаем веб-морду
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
