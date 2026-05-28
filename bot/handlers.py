# ==========================================
# Файл: bot/handlers.py
# Справка: README.md → Бот / Обработчики
# Задача: регистрация обработчиков и потоков
# ==========================================

import os
from ping_utils import start_background_pinger
from services.agent_pinger import start_agent_pinger
from services.log_cleaner import start_log_cleaner
from .handlers import register_handlers
from dialogue.callbacks import register_callback_handlers
from services.autoposter import start_autoposter

def register_all_handlers(bot, config):
    register_handlers(bot, config)
    register_callback_handlers(bot, config)
    start_background_pinger(60)
    start_agent_pinger()
    start_log_cleaner()
    if config.get("autoposter", {}).get("enabled", True):
        start_autoposter(config, os.environ.get("VK_TOKEN"), os.environ.get("VK_OWNER_ID"))
