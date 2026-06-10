# ==========================================
# Файл: services/adaptive_modes.py
# Справка: README.md → Адаптивные режимы (сервисный слой)
# Задача: тонкая обёртка над dialogue/adaptive_modes для веб-морды и роутинга
# Добавляет: get_current_mode_for_routing()
# Используется: routing_engine.py, web_api/modes.py
# ==========================================

from dialogue.adaptive_modes import (
    # Основные функции
    get_current_adaptive_mode,
    get_adaptive_quotes_interval,
    get_adaptive_publisher_interval,
    should_adaptive_publish,
    set_adaptive_enabled,
    reset_to_etalon,
    load_adaptive_config,
    save_adaptive_config,
    # Константы
    ADAPTIVE_ENABLED,
    ADAPTIVE_COOLDOWN,
    DEADEND_TIMEOUT
)

def get_current_mode_for_routing():
    """
    Возвращает текущий режим для routing_engine.
    Если адаптивные режимы включены — возвращает адаптивный.
    Иначе — эталонный по времени.
    """
    return get_current_adaptive_mode()
