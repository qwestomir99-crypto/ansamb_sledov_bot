# ==========================================
# Файл: bot/handlers/__init__.py
# Справка: README.md → Обработчики команд / Сборка
# Задача: собирает все модули handlers и запускает потоки
# Комментарий: VK_READER_TOKEN (короткий) → vk_reader_loop, VK_TOKEN (длинный) → publish_loop и autoposter
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
    from dialogue.vk_reader import vk_reader_loop
    
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    admin_id = int(os.environ.get("ADMIN_USER_ID", 0))
    
    # Ключи VK — каждый для своего дела
    vk_token = os.environ.get("VK_TOKEN")              # длинный, 85+ — для публикации в группу
    vk_reader_token = os.environ.get("VK_READER_TOKEN") # короткий, 71 — для чтения стены
    vk_group_id = os.environ.get("VK_GROUP_ID")         # ID сообщества — для публикации в группу
    vk_owner_id = os.environ.get("VK_OWNER_ID")         # твой личный ID — для VK Reader
    
    # Потоки
    threading.Thread(target=scheduler_loop, args=(bot, tg_chat_id, admin_id), daemon=True).start()
    threading.Thread(target=quotes_loop, args=(bot, tg_chat_id), daemon=True).start()
    threading.Thread(target=publish_loop, args=(bot, vk_token, vk_group_id, tg_chat_id), daemon=True).start()
    threading.Thread(target=vk_reader_loop, args=(bot, vk_reader_token, vk_owner_id, tg_chat_id), daemon=True).start()
    
    if config.get("autoposter", {}).get("enabled", True):
        threading.Thread(target=start_autoposter, args=(config, vk_token, vk_group_id), daemon=True).start()
    
    print("[HANDLERS] Все потоки запущены: ритуал, цитаты, пул, YouTube, VK Reader")
