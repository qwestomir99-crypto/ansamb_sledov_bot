# ==========================================
# Файл: bot/handlers/__init__.py
# Справка: README.md → Обработчики команд / Сборка
# Задача: собирает все модули handlers
# Комментарий: основной обработчик — dialogue/handlers.py
# ==========================================

import os
import threading
import telebot
from debug_utils import debug_log

def register_handlers(bot: telebot.TeleBot, config: dict):
    from dialogue.handlers import register_handlers as register_dialogue_handlers
    register_dialogue_handlers(bot, config)
    
    from .start import register_start_handler
    from .help import register_help_handler
    from .debug import register_debug_handler
    from .youtube_test import register_youtube_test_handler
    from .flash import register_flash_handler
    from .reset import register_reset_handler
    from .mood import register_mood_handler
    from .ping import register_ping_handler
    
    register_start_handler(bot, config)
    register_help_handler(bot, config)
    register_debug_handler(bot, config)
    register_youtube_test_handler(bot, config)
    register_flash_handler(bot, config)
    register_reset_handler(bot, config)
    register_mood_handler(bot, config)
    register_ping_handler(bot, config)
    
    debug_log("HANDLERS", "Все обработчики команд зарегистрированы", "INFO")


def register_all_handlers(bot, config):
    from dialogue.callbacks import register_callback_handlers
    from dialogue.scheduler import scheduler_loop
    from dialogue.quotes import quotes_loop
    from dialogue.publisher import publish_loop
    from services.autoposter import start_autoposter
    
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    admin_id = int(os.environ.get("ADMIN_USER_ID", 0))
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    threading.Thread(target=scheduler_loop, args=(bot, tg_chat_id, admin_id), daemon=True).start()
    threading.Thread(target=quotes_loop, args=(bot, tg_chat_id), daemon=True).start()
    threading.Thread(target=publish_loop, args=(bot, vk_token, vk_owner_id, tg_chat_id), daemon=True).start()
    
    if config.get("autoposter", {}).get("enabled", True):
        threading.Thread(target=start_autoposter, args=(config, vk_token, vk_owner_id), daemon=True).start()
    
    print("[HANDLERS] Все потоки запущены: ритуал, цитаты, пул, YouTube")
