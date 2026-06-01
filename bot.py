# ==========================================
# Файл: bot.py
# Справка: README.md → Бот / Точка входа
# Задача: запуск бота и веб-морды
# ==========================================

import threading
from services.app import app
from bot.main import main

# Запуск веб-морды в фоновом потоке
def run_web():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    main()
