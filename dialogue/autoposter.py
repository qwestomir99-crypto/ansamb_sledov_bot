import time
import threading
import requests
from dialogue.publisher_utils import post_to_vk

# ID групп (берём из config.json, но пока укажем явно)
SOURCE_CHAT_ID = -1003952512259  # Ансамбль: След на контакте
TARGET_CHAT_ID = "@саперы_аутентичности"  # Сапёры Аутентичности

def setup_autoposter(bot, vk_token, vk_owner_id, admin_id):
    """
    Настраивает обработчик сообщений для автопостинга.
    Вызывается из bot.py после инициализации бота.
    """
    
    @bot.message_handler(func=lambda msg: msg.chat.id == SOURCE_CHAT_ID and msg.from_user.id == admin_id)
    def autopost(message):
        text = message.text
        if not text or text.startswith('/') or text.startswith('#'):
            # Игнорируем команды и пустые сообщения
            return
        
        # 1. Отправляем копию в группу «Сапёры»
        try:
            bot.send_message(TARGET_CHAT_ID, text, parse_mode='Markdown')
            print(f"[AUTOPOSTER] Отправлено в Сапёры: {text[:50]}...")
        except Exception as e:
            print(f"[AUTOPOSTER] Ошибка отправки в Сапёры: {e}")
        
        # 2. Отправляем в VK (если есть токен)
        if vk_token:
            tags = "#Ансамбль #СледНаКонтаке"
            ok = post_to_vk(text, tags, vk_token, vk_owner_id)
            if ok:
                print(f"[AUTOPOSTER] Отправлено в VK")
            else:
                print(f"[AUTOPOSTER] Ошибка отправки в VK")
    
    print(f"[AUTOPOSTER] Автопостинг настроен: {SOURCE_CHAT_ID} → {TARGET_CHAT_ID} + VK")
