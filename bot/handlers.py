# ==========================================
# Файл: bot/handlers.py
# Справка: README.md → Бот / Обработчики
# Задача: регистрация обработчиков и потоков
# ==========================================

import os
import threading
from .handlers import register_handlers
from dialogue.callbacks import register_callback_handlers
from dialogue.scheduler import scheduler_loop
from dialogue.quotes import quotes_loop

def register_all_handlers(bot, config):
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    admin_id = int(os.environ.get("ADMIN_USER_ID", 0))
    
    # Полуночный ритуал
    threading.Thread(target=scheduler_loop, args=(bot, tg_chat_id, admin_id), daemon=True).start()
    
    # Цитаты
    threading.Thread(target=quotes_loop, args=(bot, tg_chat_id), daemon=True).start()
    
    print("[HANDLERS] Обработчики и потоки запущены")
