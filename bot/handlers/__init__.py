# ==========================================
# Файл: bot/handlers/__init__.py
# Справка: README.md → Обработчики команд / Сборка
# Задача: собирает все модули handlers в единый регистратор
# Комментарий: импортирует и экспортирует register_handlers и register_all_handlers
# ==========================================

import telebot
from debug_utils import debug_log

def register_handlers(bot: telebot.TeleBot, config: dict):
    from .start import register_start_handler
    from .help import register_help_handler
    from .menu import register_menu_handler
    from .debug import register_debug_handler
    from .youtube_test import register_youtube_test_handler
    from .talk import register_talk_handler
    from .rituals import register_rituals_handler
    from .flash import register_flash_handler
    from .reset import register_reset_handler
    from .mood import register_mood_handler
    from .ping import register_ping_handler
    from .unknown import register_unknown_handler
    
    # ==========================================
    # ПРЯМАЯ РЕГИСТРАЦИЯ #АДМИН (без admin.py)
    # ==========================================
    @bot.message_handler(func=lambda message: message.text.startswith("#админ"))
    def handle_admin(message):
        try:
            from dialogue.admin_commands import handle_admin_command
            handle_admin_command(message, bot)
        except Exception as e:
            debug_log("ADMIN", f"Ошибка в handle_admin: {e}", "ERROR")
            bot.reply_to(message, "❌ Ошибка при открытии админ-панели")
    
    # ==========================================
    # РЕГИСТРАЦИЯ ВСЕХ ОСТАЛЬНЫХ ОБРАБОТЧИКОВ
    # ==========================================
    register_start_handler(bot, config)
    register_help_handler(bot, config)
    register_menu_handler(bot, config)
    register_debug_handler(bot, config)
    register_youtube_test_handler(bot, config)
    register_talk_handler(bot, config)
    register_rituals_handler(bot, config)
    register_flash_handler(bot, config)
    register_reset_handler(bot, config)
    register_mood_handler(bot, config)
    register_ping_handler(bot, config)
    register_unknown_handler(bot, config)
    
    debug_log("HANDLERS", "Все обработчики команд зарегистрированы", "INFO")


def register_all_handlers(bot, config):
    """Алиас для register_handlers + колбэки и потоки"""
    import os
    import threading
    from ping_utils import start_background_pinger
    from services.agent_pinger import start_agent_pinger
    from services.log_cleaner import start_log_cleaner
    from dialogue.callbacks import register_callback_handlers
    from services.autoposter import start_autoposter
    from dialogue.scheduler import scheduler_loop
    from dialogue.publisher import publish_loop
    from dialogue.quotes import quotes_loop
    
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    
    start_background_pinger(60)
    start_agent_pinger()
    start_log_cleaner()
    
    if config.get("autoposter", {}).get("enabled", True):
        start_autoposter(config, os.environ.get("VK_TOKEN"), os.environ.get("VK_OWNER_ID"))
    
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    admin_id = int(os.environ.get("ADMIN_USER_ID", 0))
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    threading.Thread(target=scheduler_loop, args=(bot, tg_chat_id, admin_id), daemon=True).start()
    threading.Thread(target=publish_loop, args=(bot, vk_token, vk_owner_id, tg_chat_id), daemon=True).start()
    threading.Thread(target=quotes_loop, args=(bot, tg_chat_id), daemon=True).start()
    
    print("[HANDLERS] Все потоки запущены")
