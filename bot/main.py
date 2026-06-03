# ==========================================
# Файл: bot/main.py
# Справка: README.md → Бот / Запуск
# Задача: запуск бота + сохранение сообщений в SQLite
# ==========================================

import time
from .core import load_config, get_bot
from .handlers import register_handlers
from dialogue.message_dispatcher import register_dispatcher
from services.sqlite_client import save_message
from evolve_agent import start_evolution_scheduler

def main():
    config = load_config()
    bot = get_bot()
    
    register_handlers(bot, config)
    register_dispatcher(bot)  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
    
    @bot.message_handler(func=lambda message: True)
    def save_all_messages(message):
        save_message(message.chat.id, message.text, source="tg")
    
    start_evolution_scheduler()
    
    try:
        bot.delete_webhook()
        print("[MAIN] Webhook удалён")
    except:
        pass
    
    print("[MAIN] Запуск polling")
    bot.polling()

if __name__ == "__main__":
    main()
