# ==========================================
# Файл: bot/handlers.py
# Справка: README.md → Бот / Обработчики
# Задача: регистрация обработчиков и потоков
# Комментарий: VK_READER_TOKEN для ридера, VK_TOKEN для постинга
# ==========================================

import os
import threading
from ping_utils import start_background_pinger
from services.agent_pinger import start_agent_pinger
from .handlers import register_handlers
from dialogue.callbacks import register_callback_handlers
from dialogue.scheduler import scheduler_loop
from dialogue.quotes import quotes_loop
from dialogue.publisher import publish_loop
from services.autoposter import start_autoposter
from dialogue.vk_reader import vk_reader_loop

def register_all_handlers(bot, config):
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    
    start_background_pinger(60)
    start_agent_pinger()
    
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    admin_id = int(os.environ.get("ADMIN_USER_ID", 0))
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    vk_reader_token = os.environ.get("VK_READER_TOKEN")
    
    threading.Thread(target=scheduler_loop, args=(bot, tg_chat_id, admin_id), daemon=True).start()
    threading.Thread(target=quotes_loop, args=(bot, tg_chat_id), daemon=True).start()
    threading.Thread(target=publish_loop, args=(bot, vk_token, vk_owner_id, tg_chat_id), daemon=True).start()
    threading.Thread(target=vk_reader_loop, args=(bot, vk_reader_token, vk_owner_id, tg_chat_id), daemon=True).start()
    
    if config.get("autoposter", {}).get("enabled", True):
        threading.Thread(target=start_autoposter, args=(config, vk_token, vk_owner_id), daemon=True).start()
    
    print("[HANDLERS] Все потоки запущены")
