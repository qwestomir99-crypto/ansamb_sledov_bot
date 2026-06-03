# ==========================================
# Файл: dialogue/publisher.py
# Справка: README.md → Публикатор
# Задача: публикация постов (немедленная и отложенная)
# Комментарий: поддерживает Telegram и VK, теги, фото, видео
# ==========================================

import os
import json
from debug_utils import debug_log
from dialogue.publisher_utils import post_to_telegram, post_to_vk

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def publish_post_immediately(bot, chat_id, text, tags_str, file_id=None):
    """
    Публикует пост немедленно в Telegram и VK
    """
    config = load_config()
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    success_tg = False
    success_vk = False
    
    # Публикуем в Telegram
    if tg_chat_id:
        success_tg = post_to_telegram(bot, tg_chat_id, text, file_id, tags_str)
        debug_log("PUBLISH", f"Telegram: {'✅' if success_tg else '❌'}")
    
    # Публикуем в VK
    if vk_token and vk_owner_id:
        success_vk, _ = post_to_vk(text, tags_str, vk_token, vk_owner_id, file_id)
        debug_log("PUBLISH", f"VK: {'✅' if success_vk else '❌'}")
    
    return success_tg or success_vk

def publish_delayed(bot, text, tags_str, delay_seconds, file_id=None):
    """
    Отложенная публикация (сохраняет в очередь)
    """
    # TODO: реализовать сохранение в post_pool.json и запуск publisher_loop
    pass
