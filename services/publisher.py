# ==========================================
# Файл: services/publisher.py
# Справка: README.md → Публикатор
# Задача: публикация постов с маршрутизацией на основе аналитики
# Комментарий: заменяет статическую маршрутизацию на вызов routing_engine.py
# Зависит от: routing_engine, tg_api, vk_api, debug_utils
# Вызывается из: bot.py (обработчик публикации)
# ==========================================

from services.routing_engine import decide_target
from services.tg_api import send_telegram_message
from services.vk_api import send_vk_post
from debug_utils import debug_log

def log_pub(level, message):
    debug_log("PUBLISHER", message, level)

def publish_post(post_text, user_id=None):
    """
    Публикует пост с маршрутизацией на основе аналитики.
    """
    # 1. Определяем целевой канал
    target = decide_target(post_text, user_id)
    log_pub("INFO", f"Решение: {target}")
    
    # 2. Публикуем в зависимости от target
    if target == "none":
        log_pub("INFO", "Публикация отложена (режим тишины)")
        return
    
    if target == "personal" or target == "both":
        send_telegram_message(post_text)
        log_pub("INFO", "Опубликовано в личный канал")
    
    if target == "group" or target == "both":
        send_vk_post(post_text)
        log_pub("INFO", "Опубликовано в группу VK")
