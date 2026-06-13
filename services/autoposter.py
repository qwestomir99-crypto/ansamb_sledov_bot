# ==========================================
# Файл: services/autoposter.py
# Справка: README.md → Автопостинг YouTube
# Задача: публикация случайного видео из плейлиста в TG и VK
# Комментарий: TG всегда, VK в группу с VK_TOKEN + VK_GROUP_ID, цитаты из publisher_utils
# ==========================================

import sys
import os
import time
from debug_utils import debug_log
from dialogue.youtube_auto import get_random_video
from dialogue.publisher_utils import get_random_quote, post_to_vk

# ===== ЗАГРУЗКА СЕКРЕТОВ ИЗ БД =====
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.secrets_manager import get_secret
# ===================================

def log_auto(level, message):
    debug_log("AUTOPOSTER", message, level)

def check_and_publish(bot, tg_chat_id):
    log_auto("INFO", "Проверка видео из плейлиста...")
    
    video = get_random_video()
    if not video:
        log_auto("WARNING", "Не удалось получить видео из плейлиста")
        return
    
    log_auto("INFO", f"Получено видео: {video['title'][:50]}...")
    
    quote = get_random_quote()
    full_text = f"📜 {quote}\n\n🎬 {video['title']}\n{video['url']}"
    
    # TG
    try:
        bot.send_message(tg_chat_id, full_text)
        log_auto("INFO", f"Видео опубликовано в TG: {video['title'][:50]}...")
    except Exception as e:
        log_auto("ERROR", f"Ошибка TG: {e}")
    
    # VK
    vk_token = get_secret("VK_TOKEN")
    vk_owner_id = get_secret("VK_GROUP_ID")
    if vk_token and vk_owner_id:
        try:
            success, _ = post_to_vk(full_text, "", vk_token, vk_owner_id)
            if success:
                log_auto("INFO", "Видео опубликовано в VK")
            else:
                log_auto("WARNING", "VK не опубликовано")
        except Exception as e:
            log_auto("ERROR", f"Ошибка VK: {e}")

def start_autoposter(config=None, vk_token=None, vk_owner_id=None):
    log_auto("INFO", "Автопостинг YouTube запущен (TG + VK, раз в день)")
    from bot.core import get_bot
    bot_instance = get_bot()
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir") if config else "@qwestomir"
    
    while True:
        try:
            check_and_publish(bot_instance, tg_chat_id)
        except Exception as e:
            log_auto("ERROR", f"Ошибка в цикле: {e}")
        time.sleep(86400)
