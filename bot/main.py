# ==========================================
# Файл: bot/main.py
# Справка: README.md → Бот / Запуск
# Задача: запуск бота (точка входа)
# ==========================================

import time
from .core import load_config, get_bot, global_exception_handler, thread_exception_handler
from .handlers import register_handlers

def main():
    config = load_config()
    bot = get_bot()
    register_handlers(bot, config)
    print("Бот запущен. Ритм 0,8 Гц.")
    bot.polling()

if __name__ == "__main__":
    main()
