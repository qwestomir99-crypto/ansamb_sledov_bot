# ==========================================
# Файл: bot/handlers.py
# Справка: README.md → Бот / Обработчики
# Задача: регистрация обработчиков и потоков
# ==========================================

import os
import threading
from ping_utils import start_background_pinger
from services.agent_pinger import start_agent_pinger
from services.log_cleaner import start_log_cleaner
from .handlers import register_handlers
from dialogue.callbacks import register_callback_handlers
from services.autoposter import start_autoposter
from dialogue.scheduler import scheduler_loop
from dialogue.publisher import publish_loop

def register_all_handlers(bot, config):
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    
    # Запуск фоновых задач
    start_background_pinger(60)
    start_agent_pinger()
    start_log_cleaner()
    
    # Автопостер (YouTube)
    if config.get("autoposter", {}).get("enabled", True):
        start_autoposter(config, os.environ.get("VK_TOKEN"), os.environ.get("VK_OWNER_ID"))
    
    # Полуночный ритуал
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    admin_id = int(os.environ.get("ADMIN_USER_ID", 0))
    scheduler_thread = threading.Thread(target=scheduler_loop, args=(bot, tg_chat_id, admin_id), daemon=True)
    scheduler_thread.start()
    
    # ==========================================
    # ПУБЛИКАТОР ПОСТОВ (из dialogue/publisher.py)
    # ==========================================
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    publisher_thread = threading.Thread(
        target=publish_loop,
        args=(bot, vk_token, vk_owner_id, tg_chat_id),
        daemon=True
    )
    publisher_thread.start()
    print("[HANDLERS] Публикатор постов запущен")
