# ==========================================
# Файл: new_debugger/dialogue/shabbat_manager.py
# Справка: README.md → Управление Шаббатом
# Задача: определяет, сейчас ли Шаббат (для Москвы)
# Комментарий: Использует Hebcal API, координаты Москвы
# Зависит от: requests, json, datetime
# Вызывается из: activity_modes.py
# ==========================================

import os
import json
import requests
from datetime import datetime
from debug_utils import debug_log

CONFIG_FILE = "config.json"
SHABBAT_CACHE_FILE = "dialogue/data/shabbat_cache.json"

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
        "dt": datetime.now().strftime("%Y-%m-%d")
    }
    
    try:
        r = requests.get(url, params=params, timeout=30)
        if r.status_code == 200:
            data = r.json()
            times = data.get('times', {})
            shabbat_start = datetime.fromisoformat(times.get('sunset', '').replace('Z', '+00:00'))
            shabbat_end = datetime.fromisoformat(times.get('tzeit', '').replace('Z', '+00:00'))
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
                return datetime.fromisoformat(data['start']), datetime.fromisoformat(data['end'])
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
    """Возвращает True, если сейчас Шаббат"""
    lat, lon = get_coordinates()
    now = datetime.now()
    
    start, end = load_cached_times()
    if start and end and start.date() == now.date():
        return start <= now <= end
    
    # Кэш устарел — обновляем
    start, end = fetch_shabbat_times(lat, lon)
    if start and end:
        save_cached_times(start, end)
        return start <= now <= end
    
    debug_log("SHABBAT", "Не удалось получить время Шаббата", "WARNING")
    return False

if __name__ == "__main__":
    print("Шаббат сейчас?" , is_shabbat())
