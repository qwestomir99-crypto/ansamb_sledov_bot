# ==========================================
# Файл: dialogue/shabbat_manager.py
# Справка: README.md → Управление Шаббатом
# Задача: определяет, сейчас ли Шаббат (с учётом координат и +72 минут)
# Комментарий: использует локальную библиотеку hebcal (без внешних API)
# Зависит от: hebcal, datetime, pytz
# Вызывается из: activity_modes.py
# ==========================================

import pytz
from datetime import datetime
from debug_utils import debug_log

# Подключаем библиотеку hebcal (ставится через pip install hebcal)
try:
    import hebcal
    from hebcal.util.location import get_location
    HEBICAL_AVAILABLE = True
    debug_log("SHABBAT", "Библиотека hebcal загружена", "INFO")
except ImportError:
    HEBICAL_AVAILABLE = False
    debug_log("SHABBAT", "Библиотека hebcal не найдена, Шаббат отключён", "ERROR")

MOSCOW_TZ = pytz.timezone('Europe/Moscow')
MOSCOW_LAT = 55.7558
MOSCOW_LON = 37.6173

def is_shabbat():
    """
    Возвращает True, если сейчас Шаббат (с учётом захода солнца и +72 минут).
    """
    if not HEBICAL_AVAILABLE:
        return False
    
    try:
        # Получаем локальное время с учётом координат
        timezone = get_location(latitude=MOSCOW_LAT, longitude=MOSCOW_LON)
        time_info = hebcal.TimeInfo.now(
            timezone=timezone,
            latitude=MOSCOW_LAT,
            longitude=MOSCOW_LON
        )
        
        # Флаг Шаббата (учитывает все правила + добавленные минуты)
        is_shabbat_flag = getattr(time_info, 'is_shabbat', None)
        if is_shabbat_flag is not None:
            if is_shabbat_flag():
                debug_log("SHABBAT", "Шаббат (по расчёту hebcal)", "INFO")
                return True
        
        # Альтернативный способ: проверяем, что сегодня суббота и уже зашло солнце
        if time_info.is_shabbat():
            debug_log("SHABBAT", "Шаббат (по is_shabbat)", "INFO")
            return True
            
    except Exception as e:
        debug_log("SHABBAT", f"Ошибка расчёта: {e}", "ERROR")
        return False
    
    debug_log("SHABBAT", "Не Шаббат", "INFO")
    return False

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("Шаббат сейчас?", is_shabbat())
