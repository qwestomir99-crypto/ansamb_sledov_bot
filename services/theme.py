# ==========================================
# Файл: services/theme.py
# Справка: README.md → Веб-морда / Темы
# Задача: определение темы по времени, сохранение выбора пользователя
# Комментарий: используется в app.py и web_api.py
# Зависит от: pytz, datetime, os
# Вызывается из: services/app.py, services/web_api.py
# ==========================================

import os
import datetime
import pytz
import json

THEME_FILE = "data/theme_preference.json"

def get_theme_by_time():
    """Возвращает тему в зависимости от времени суток (по Москве)"""
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.datetime.now(tz)
    hour = now.hour
    return "macos.css" if 6 <= hour < 18 else "dark.css"

def get_saved_theme():
    """Возвращает сохранённую тему пользователя (из файла)"""
    try:
        if os.path.exists(THEME_FILE):
            with open(THEME_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("theme")
    except:
        pass
    return None

def save_theme(theme):
    """Сохраняет тему пользователя в файл"""
    os.makedirs(os.path.dirname(THEME_FILE), exist_ok=True)
    with open(THEME_FILE, "w", encoding="utf-8") as f:
        json.dump({"theme": theme}, f)

def get_current_theme():
    """
    Возвращает текущую тему:
    - если есть сохранённая — её
    - иначе по времени суток
    """
    saved = get_saved_theme()
    if saved:
        return saved
    return get_theme_by_time()
