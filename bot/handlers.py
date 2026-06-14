# ==========================================
# Файл: bot/handlers.py
# Справка: README.md → Бот / Обработчики
# Задача: регистрация обработчиков и потоков
# Комментарий: ридер: VK_READER_TOKEN + VK_OWNER_ID, постинг: VK_TOKEN + VK_GROUP_ID
# ==========================================

import os
import json
import threading
from datetime import datetime
from ping_utils import start_background_pinger
from services.agent_pinger import start_agent_pinger
from .handlers import register_handlers
from dialogue.callbacks import register_callback_handlers
from dialogue.scheduler import scheduler_loop
from dialogue.quotes import quotes_loop
from dialogue.publisher import publish_loop
from services.autoposter import start_autoposter
from dialogue.vk_reader import vk_reader_loop

# ==========================================
# 1. АВТОСОЗДАНИЕ И АВТОИСПРАВЛЕНИЕ КОНФИГА
# ==========================================

def ensure_config_exists():
    """Проверяет наличие config.json и создаёт его с дефолтами, если нет"""
    config_path = 'dialogue/data/config.json'
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    if not os.path.exists(config_path):
        default_config = {
            "VK_READER_TOKEN": "",
            "TG_TOKEN": "",
            "OWNER_ID": 0,
            "TG_CHAT_ID": 0,
            "VK_GROUP_ID": 0,
            "telegram": {
                "publish_channel": "@qwestomir"
            },
            "autoposter": {
                "enabled": True
            },
            "created_at": datetime.now().isoformat(),
            "auto_created": True
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        print(f"✅ config.json автосоздан: {config_path}")
    return config_path

def load_config_safe():
    """Загружает конфиг с автоисправлением"""
    config_path = ensure_config_exists()
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                raise ValueError("Конфиг пуст")
            return json.loads(content)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"⚠️ Ошибка чтения конфига: {e}, пересоздаю...")
        default_config = {
            "VK_READER_TOKEN": "",
            "TG_TOKEN": "",
            "OWNER_ID": 0,
            "TG_CHAT_ID": 0,
            "VK_GROUP_ID": 0,
            "telegram": {
                "publish_channel": "@qwestomir"
            },
            "autoposter": {
                "enabled": True
            },
            "created_at": datetime.now().isoformat(),
            "auto_recreated": True,
            "error": str(e)
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        return default_config

# ==========================================
# 2. УНИВЕРСАЛЬНЫЕ ЗАЩИТНИКИ (типы из env)
# ==========================================

def safe_get_str(env_var, default=""):
    """Безопасное получение строки из окружения"""
    value = os.environ.get(env_var, default)
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    return str(value)

def safe_get_int(env_var, default=0):
    """Безопасное получение числа из окружения"""
    value = os.environ.get(env_var, str(default))
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# ==========================================
# 3. ГЛАВНЫЙ ОБРАБОТЧИК
# ==========================================

def register_all_handlers(bot, config=None):
    # Если config не передан — загружаем его безопасно
    if config is None:
        config = load_config_safe()
    
    # Регистрация обработчиков команд и кнопок
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    
    # Запуск пингеров
    start_background_pinger(60)
    start_agent_pinger()
    
    # Параметры из конфига и окружения — ТОЛЬКО ЧЕРЕЗ ЗАЩИТНИКИ
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    admin_id = safe_get_int("ADMIN_USER_ID", 0)
    
    # Для постинга в группу (VK)
    vk_token = safe_get_str("VK_TOKEN", "")
    vk_group_id = safe_get_str("VK_GROUP_ID", "")
    
    # Для чтения личного профиля (VK Reader)
    vk_reader_token = safe_get_str("VK_READER_TOKEN", "")
    vk_owner_id = safe_get_int("VK_OWNER_ID", 0)
    
    # ДИАГНОСТИКА
    print(f"🔍 VK_READER_TOKEN: тип={type(vk_reader_token)}, длина={len(vk_reader_token)}")
    print(f"🔍 VK_OWNER_ID: тип={type(vk_owner_id)}, значение={vk_owner_id}")
    print(f"🔍 TG_CHAT_ID: тип={type(tg_chat_id)}, значение={tg_chat_id}")
    
    # Запуск потоков
    threading.Thread(target=scheduler_loop, args=(bot, tg_chat_id, admin_id), daemon=True).start()
    threading.Thread(target=quotes_loop, args=(bot, tg_chat_id), daemon=True).start()
    threading.Thread(target=publish_loop, args=(bot, vk_token, vk_group_id, tg_chat_id), daemon=True).start()
    threading.Thread(target=vk_reader_loop, args=(bot, vk_reader_token, vk_owner_id, tg_chat_id), daemon=True).start()
    
    if config.get("autoposter", {}).get("enabled", True):
        threading.Thread(target=start_autoposter, args=(config, vk_token, vk_group_id), daemon=True).start()
    
    print("[HANDLERS] Все потоки запущены: ридер, постинг, цитаты, пул, автопостер")

# ==========================================
# 4. ТЕСТ
# ==========================================

if __name__ == "__main__":
    print("=== ТЕСТ HANDLERS ===")
    config = load_config_safe()
    print(f"Конфиг загружен: {json.dumps(config, indent=2)[:200]}...")
    print("✅ handlers.py готов к работе")
