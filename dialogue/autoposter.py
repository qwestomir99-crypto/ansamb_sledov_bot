import time
import threading
import requests
from dialogue.publisher_utils import post_to_telegram, post_to_vk

def setup_autoposter(bot, config, vk_token, vk_owner_id):
    """
    Настраивает обработчик сообщений для автопостинга.
    Все ID и настройки берутся из config.json.
    """
    # Берём настройки из конфига
    autoposter_config = config.get("autoposter", {})
    source_chat_id = autoposter_config.get("source_chat_id")
    target_chat_id = autoposter_config.get("target_chat_id")
    admin_id = config.get("telegram", {}).get("admin_user_id")
    
    if not source_chat_id or not target_chat_id or not admin_id:
        print("[AUTOPOSTER] Ошибка: не хватает настроек в config.json")
        return
    
    @bot.message_handler(func=lambda msg: msg.chat.id == source_chat_id and msg.from_user.id == admin_id)
    def autopost(message):
        text = message.text
        if not text or text.startswith('/') or text.startswith('#'):
            return
        
        # Отправляем в Telegram через общую функцию
        try:
            post_to_telegram(bot, target_chat_id, text, file_path=None, tags=None)
            print(f"[AUTOPOSTER] Отправлено в Telegram: {target_chat_id}")
        except Exception as e:
            print(f"[AUTOPOSTER] Ошибка Telegram: {e}")
        
        # Отправляем в VK, если включено
        if vk_token and autoposter_config.get("vk_enabled", True):
            tags = autoposter_config.get("vk_tags", "#Ансамбль #СледНаКонтаке")
            try:
                ok = post_to_vk(text, tags, vk_token, vk_owner_id, file_path=None)
                if ok:
                    print(f"[AUTOPOSTER] Отправлено в VK")
            except Exception as e:
                print(f"[AUTOPOSTER] Ошибка VK: {e}")
    
    print(f"[AUTOPOSTER] Автопостинг настроен: {source_chat_id} → {target_chat_id} + VK")
