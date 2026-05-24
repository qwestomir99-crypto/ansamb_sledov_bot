# ==========================================
# Файл: dialogue/shabbat_manager.py
# Справка: README.md → Управление Шаббатом
# Задача: определяет, сейчас ли Шаббат (для Москвы)
# Комментарий: использует Hebcal API, координаты Москвы.
#              Если API недоступен — возвращает False (режим покоя не активируется).
# Зависит от: requests, json, datetime, pytz
# Вызывается из: activity_modes.py
# ==========================================

import os
import json
import requests
from datetime import datetime
import pytz
from debug_utils import debug_log

CONFIG_FILE = "config.json"
SHABBAT_CACHE_FILE = "dialogue/data/shabbat_cache.json"

# Часовой пояс Москвы
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# Координаты Москвы (по умолчанию)
MOSCOW_LAT = 55.7558
MOSCOW_LON = 37.6173

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def get_coordinates():
    """Возвращает координаты из config.json или координаты Москвы"""
    config = load_config()
    location = config.get("location", {})
    lat = location.get("latitude", MOSCOW_LAT)
    lon = location.get("longitude", MOSCOW_LON)
    return lat, lon

def fetch_shabbat_times(lat, lon):
    """Запрашивает у Hebcal API время начала и окончания Шаббата"""
    debug_log("SHABBAT", f"Запрос времени Шаббата для координат: {lat}, {lon}")
    url = "https://www.hebcal.com/zmanim"
    params = {
        "cfg": "json",
        "im": "1",
        "lat": lat,
        "lng": lon,
        "tzid": "Europe/Moscow",
        "dt": datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d")
    }
    
    try:
        r = requests.get(url, params=params, timeout=30)
        if r.status_code == 200:
            data = r.json()
            times = data.get('times', {})
            shabbat_start = datetime.fromisoformat(times.get('sunset', '').replace('Z', '+00:00'))
            shabbat_end = datetime.fromisoformat(times.get('tzeit', '').replace('Z', '+00:00'))
            # Преобразуем в московский часовой пояс (на случай, если API вернул UTC)
            shabbat_start = shabbat_start.astimezone(MOSCOW_TZ)
            shabbat_end = shabbat_end.astimezone(MOSCOW_TZ)
            debug_log("SHABBAT", f"Шаббат: {shabbat_start} → {shabbat_end}")
            return shabbat_start, shabbat_end
        else:
            debug_log("SHABBAT", f"Ошибка API: {r.status_code}", "ERROR")
            return None, None
    except Exception as e:
        debug_log("SHABBAT", f"Ошибка запроса: {e}", "ERROR")
        return None, None

def load_cached_times():
    if os.path.exists(SHABBAT_CACHE_FILE):
        try:
            with open(SHABBAT_CACHE_FILE, "r") as f:
                data = json.load(f)
                start = datetime.fromisoformat(data['start'])
                end = datetime.fromisoformat(data['end'])
                # Приводим к московскому часовому поясу
                start = start.astimezone(MOSCOW_TZ) if start.tzinfo else MOSCOW_TZ.localize(start)
                end = end.astimezone(MOSCOW_TZ) if end.tzinfo else MOSCOW_TZ.localize(end)
                return start, end
        except:
            pass
    return None, None

def save_cached_times(start, end):
    try:
        os.makedirs(os.path.dirname(SHABBAT_CACHE_FILE), exist_ok=True)
        with open(SHABBAT_CACHE_FILE, "w") as f:
            json.dump({"start": start.isoformat(), "end": end.isoformat()}, f)
    except Exception as e:
        debug_log("SHABBAT", f"Ошибка сохранения кэша: {e}", "ERROR")

def is_shabbat():
    """
    Возвращает True, если сейчас Шаббат (по Москве).
    Если API не ответил — возвращает False (безопасный режим: не блокируем работу).
    """
    lat, lon = get_coordinates()
    now_moscow = datetime.now(MOSCOW_TZ)
    
    start, end = load_cached_times()
    if start and end and start.date() == now_moscow.date():
        return start <= now_moscow <= end
    
    # Кэш устарел — обновляем
    start, end = fetch_shabbat_times(lat, lon)
    if start and end:
        save_cached_times(start, end)
        return start <= now_moscow <= end
    
    # API не ответил — безопасный режим: Шаббат не активируем
    debug_log("SHABBAT", "Не удалось получить время Шаббата, режим покоя ОТКЛЮЧЁН (safe mode)", "WARNING")
    return False

if __name__ == "__main__":
    print("Шаббат сейчас?" , is_shabbat())
