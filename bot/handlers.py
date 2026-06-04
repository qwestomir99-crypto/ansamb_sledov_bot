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
from dialogue.publisher import publish_loop

def register_all_handlers(bot, config):
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    admin_id = int(os.environ.get("ADMIN_USER_ID", 0))
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID", "607754499")
    
    # Полуночный ритуал + эволюция
    threading.Thread(target=scheduler_loop, args=(bot, tg_chat_id, admin_id), daemon=True).start()
    
    # Цитаты по расписанию
    threading.Thread(target=quotes_loop, args=(bot, tg_chat_id), daemon=True).start()
    
    # Автопостинг из пула
    threading.Thread(target=publish_loop, args=(bot, vk_token, vk_owner_id, tg_chat_id), daemon=True).start()
    
    print("[HANDLERS] Обработчики, ритуал, цитаты и автопостинг запущены")
