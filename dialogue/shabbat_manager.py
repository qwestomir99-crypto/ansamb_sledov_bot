# ==========================================
# Файл: dialogue/shabbat_manager.py
# Справка: README.md → Управление Шаббатом
# Задача: определяет, сейчас ли Шаббат (через API hebcal)
# Комментарий: версия 2.0 — работает через официальный API, без нестабильных библиотек
# Зависит от: requests, datetime, pytz
# Вызывается из: activity_modes.py
# ==========================================

import requests
from datetime import datetime
import pytz
from debug_utils import debug_log

MOSCOW_TZ = pytz.timezone('Europe/Moscow')
MOSCOW_LAT = 55.7558
MOSCOW_LON = 37.6173

def fetch_shabbat_times():
    """Запрашивает через API времена начала и окончания Шаббата на текущие сутки"""
    today = datetime.now(MOSCOW_TZ).date()
    url = "https://www.hebcal.com/shabbat"
    params = {
        "cfg": "json",
        "gy": today.year,
        "gm": today.month,
        "gd": today.day,
        "lat": MOSCOW_LAT,
        "lng": MOSCOW_LON,
        "tzid": "Europe/Moscow",
        "havdalah": 72,      # 72 минуты для исхода
        "candle": 18         # зажигание свечей за 18 минут до захода
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        items = data.get('items', [])
        for item in items:
            if item.get('category') == 'shabbat':
                start = datetime.fromisoformat(item['date'] + 'T' + item['start']['datetime'])
                end = datetime.fromisoformat(item['date'] + 'T' + item['end']['datetime'])
                start = MOSCOW_TZ.localize(start)
                end = MOSCOW_TZ.localize(end)
                return start, end
        return None, None
    except Exception as e:
        debug_log("SHABBAT", f"Ошибка API: {e}", "ERROR")
        return None, None

def is_shabbat():
    now_moscow = datetime.now(MOSCOW_TZ)
    start, end = fetch_shabbat_times()

    if start and end:
        if start <= now_moscow <= end:
            debug_log("SHABBAT", f"Шаббат до {end.strftime('%H:%M')}", "INFO")
            return True
        else:
            debug_log("SHABBAT", "Не Шаббат", "INFO")
            return False
    else:
        debug_log("SHABBAT", "API не ответил, режим покоя отключён", "WARNING")
        return False
