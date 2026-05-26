# ==========================================
# Файл: services/theme.py
# Справка: README.md → Веб-морда / Темы
# Задача: определение темы по времени, сохранение выбора пользователя
# Комментарий: используется в app.py и web_api.py
# Зависит от: pytz, datetime, os, json
# Вызывается из: services/app.py, services/web_api.py
# ==========================================

import os
import json
import datetime
import pytz

# ==========================================
# ПУТЬ К ФАЙЛУ СОХРАНЕНИЯ
# ==========================================
THEME_FILE = "data/theme_preference.json"

# ==========================================
# ОПРЕДЕЛЕНИЕ ТЕМЫ ПО ВРЕМЕНИ
# ==========================================
def get_theme_by_time():
    """
    Возвращает тему в зависимости от времени суток (по Москве).
    Светлая тема (macos.css) с 6:00 до 18:00.
    Тёмная тема (dark.css) с 18:00 до 6:00.
    """
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.datetime.now(tz)
    hour = now.hour
    return "macos.css" if 6 <= hour < 18 else "dark.css"

# ==========================================
# СОХРАНЕНИЕ И ЗАГРУЗКА ВЫБОРА ПОЛЬЗОВАТЕЛЯ
# ==========================================
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

# ==========================================
# ОСНОВНАЯ ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ТЕМЫ
# ==========================================
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

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ ТЕМ ===")
    print(f"Тема по времени: {get_theme_by_time()}")
    print(f"Сохранённая тема: {get_saved_theme()}")
    print(f"Итоговая тема: {get_current_theme()}")
