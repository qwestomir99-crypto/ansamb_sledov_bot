# ==========================================
# Файл: bot/main.py
# Справка: README.md → Бот / Запуск
# Задача: запуск бота
# ==========================================

from .core import load_config, get_bot
from .handlers import register_handlers

def main():
    config = load_config()
    bot = get_bot()
    
    register_handlers(bot, config)
    
    print("[MAIN] Запуск polling")
    bot.polling()

if __name__ == "__main__":
    main()
