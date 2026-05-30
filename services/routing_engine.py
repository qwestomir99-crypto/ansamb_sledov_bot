# ==========================================
# Файл: services/routing_engine.py
# Справка: README.md → Маршрутизация
# Задача: принятие решения о публикации на основе аналитики
# Комментарий: связывает adaptive_modes, sql_analytics, context_mirror
# Зависит от: adaptive_modes, sql_analytics, context_mirror
# Вызывается из: publisher.py, bot.py
# ==========================================

from services.adaptive_modes import get_current_mode_for_routing
from services.sql_analytics import get_routing_context
from Alice.core import get_alice_context_for_routing

def decide_target(post_text, user_id=None):
    """
    Возвращает target: 'personal', 'group', 'both', 'none'
    """
    # 1. Получаем текущий режим
    mode = get_current_mode_for_routing()
    
    # 2. Получаем контекст из аналитики
    context = get_routing_context()
    
    # 3. Получаем контекст Алисы
    alice = get_alice_context_for_routing()
    
    # 4. Принимаем решение
    if mode == "ночь" or alice.get("tempo") == "slow":
        return "none"
    
    if context.get("activity") > 10 and alice.get("mood") == "creative":
        return "both"
    
    if "личное" in post_text.lower() or "только мне" in post_text.lower():
        return "personal"
    
    return "group"
