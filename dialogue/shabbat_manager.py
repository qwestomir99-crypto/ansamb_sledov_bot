# ==========================================
# Файл: dialogue/shabbat_manager.py
# Справка: README.md → Управление Шаббатом
# Задача: определяет, сейчас ли Шаббат (фоллбэк на дни недели)
# Комментарий: API hebcal не всегда доступен → используем день недели
#              Шаббат: пятница с 18:00 до субботы 20:00 по Москве
# Зависит от: datetime, pytz, debug_utils
# Вызывается из: quotes.py, publisher.py, autoposter.py
# ==========================================

from datetime import datetime
import pytz
from debug_utils import debug_log

MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# Время начала и конца Шаббата по Москве
SHABBAT_START_HOUR = 18  # Пятница 18:00
SHABBAT_END_HOUR = 20    # Суббота 20:00

def is_shabbat():
    """
    Проверяет, сейчас ли Шаббат.
    Фоллбэк на день недели если API недоступен.
    Шаббат: пятница 18:00 → суббота 20:00 МСК.
    """
    now = datetime.now(MOSCOW_TZ)
    weekday = now.weekday()  # 0=пн, 4=пт, 5=сб
    
    # Пятница после 18:00
    if weekday == 4 and now.hour >= SHABBAT_START_HOUR:
        return True
    
    # Суббота до 20:00
    if weekday == 5 and now.hour < SHABBAT_END_HOUR:
        return True
    
    return False
