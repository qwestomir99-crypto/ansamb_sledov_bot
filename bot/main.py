# ==========================================
# Файл: bot/main.py
# Справка: README.md → Бот / Запуск
# Задача: запуск бота + сохранение сообщений в SQLite
# Комментарий: добавлена регистрация колбэков
# ==========================================

import time
from .core import load_config, get_bot, global_exception_handler, thread_exception_handler
from .handlers import register_handlers
from dialogue.callbacks import register_callback_handlers
from services.sqlite_client import save_message

def main():
    config = load_config()
    bot = get_bot()
    
    # Регистрация обработчиков команд
    register_handlers(bot, config)
    
    # Регистрация обработчиков кнопок (колбэков)
    register_callback_handlers(bot, config)
    
    # Перехватываем сообщения и сохраняем в SQLite
    @bot.message_handler(func=lambda message: True)
    def save_all_messages(message):
        save_message(message.chat.id, message.text, source="tg")

    print("Бот запущен. Ритм 0,8 Гц.")
    bot.polling()

if __name__ == "__main__":
    main()
