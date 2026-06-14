# ==========================================
# Файл: bot/handlers.py
# Справка: README.md → Бот / Обработчики
# Задача: регистрация обработчиков и потоков
# Комментарий: ридер: VK_READER_TOKEN + VK_OWNER_ID, постинг: VK_TOKEN + VK_GROUP_ID
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
    # Регистрация обработчиков команд и кнопок
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    
    # Запуск пингеров
    start_background_pinger(60)
    start_agent_pinger()
    
    # Параметры из конфига и окружения
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    admin_id = int(os.environ.get("ADMIN_USER_ID", 0))
    
    # Для постинга в группу (VK)
    vk_token = os.environ.get("VK_TOKEN", "")
    vk_group_id = os.environ.get("VK_GROUP_ID", "")
    
    # Для чтения личного профиля (VK Reader) — с конвертацией типов!
    vk_reader_token = os.environ.get("VK_READER_TOKEN", "")
    vk_owner_id_str = os.environ.get("VK_OWNER_ID", "0")
    
    # Принудительная конвертация в нужные типы
    try:
        vk_owner_id = int(vk_owner_id_str)
    except ValueError:
        print(f"⚠️ VK_OWNER_ID не является числом ('{vk_owner_id_str}'), использую 0")
        vk_owner_id = 0
    
    # ДИАГНОСТИКА (можно убрать после отладки)
    print(f"🔍 VK_READER_TOKEN: тип={type(vk_reader_token)}, длина={len(vk_reader_token)}")
    print(f"🔍 VK_OWNER_ID: тип={type(vk_owner_id)}, значение={vk_owner_id}")
    print(f"🔍 TG_CHAT_ID: тип={type(tg_chat_id)}, значение={tg_chat_id}")
    
    # Запуск потоков
    threading.Thread(target=scheduler_loop, args=(bot, tg_chat_id, admin_id), daemon=True).start()
    threading.Thread(target=quotes_loop, args=(bot, tg_chat_id), daemon=True).start()
    threading.Thread(target=publish_loop, args=(bot, vk_token, vk_group_id, tg_chat_id), daemon=True).start()
    threading.Thread(target=vk_reader_loop, args=(bot, vk_reader_token, vk_owner_id, tg_chat_id), daemon=True).start()
    
    # Автопостер YouTube (если включён)
    if config.get("autoposter", {}).get("enabled", True):
        threading.Thread(target=start_autoposter, args=(config, vk_token, vk_group_id), daemon=True).start()
    
    print("[HANDLERS] Все потоки запущены: ридер, постинг, цитаты, пул, автопостер")

# ==========================================
# Если нужно запустить как отдельный скрипт
# ==========================================
if __name__ == "__main__":
    print("Этот файл не предназначен для прямого запуска.")
    print("Используйте bot/main.py для запуска бота.")
