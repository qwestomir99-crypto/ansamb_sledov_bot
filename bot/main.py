# ==========================================
# Файл: bot/main.py
# Справка: README.md → Бот / Запуск
# Задача: запуск бота + сохранение сообщений в SQLite
# Комментарий: загрузчик вынесен в dialogue/boot_loader.py
# ==========================================

import time
from .core import load_config, get_bot
from .handlers import register_handlers
from dialogue.callbacks import register_callback_handlers
from dialogue.message_dispatcher import register_dispatcher
from dialogue.boot_loader import get_start_mode, delete_webhook, set_webhook, wait_for_webmorda
from services.sqlite_client import save_message
from evolve_agent import start_evolution_scheduler

def main():
    config = load_config()
    bot = get_bot()
    
    # Регистрация обработчиков (всегда)
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    register_dispatcher(bot)
    
    @bot.message_handler(func=lambda message: True)
    def save_all_messages(message):
        save_message(message.chat.id, message.text, source="tg")
    
    start_evolution_scheduler()
    
    # ==========================================
    # ЗАГРУЗЧИК (выбор режима)
    # ==========================================
    mode = get_start_mode()
    
    if mode == "idle":
        print("[MAIN] Всё работает, бот в режиме ожидания")
        wait_for_webmorda(bot)
        bot.polling()
    elif mode == "restart":
        print("[MAIN] Обнаружен мёртвый webhook, удаляем...")
        delete_webhook()
        bot.polling()
    elif mode == "webhook":
        print("[MAIN] Устанавливаем webhook для вебморды")
        set_webhook()
        wait_for_webmorda(bot)
        bot.polling()
    else:  # polling
        print("[MAIN] Запуск polling (чистый старт)")
        bot.polling()

if __name__ == "__main__":
    main()
