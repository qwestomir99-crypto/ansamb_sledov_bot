# ==========================================
# Файл: services/theme.py
# Справка: README.md → Веб-морда / Темы
# Задача: определение темы, сохранение выбора, поддержка macos-new.css
# Комментарий: добавлена современная тёмная тема macos-new.css
# ==========================================

import os
import json
import datetime
import pytz

THEME_FILE = "data/theme_preference.json"

AVAILABLE_THEMES = ["macos.css", "dark.css", "macos-new.css"]

def get_theme_by_time():
    tz = pytz.timezone('Europe/Moscow')
    hour = datetime.datetime.now(tz).hour
    return "macos-new.css"  # современная тема по умолчанию

def get_saved_theme():
    try:
        if os.path.exists(THEME_FILE):
            with open(THEME_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                theme = data.get("theme")
                if theme in AVAILABLE_THEMES:
                    return theme
    except:
        pass
    return None

def save_theme(theme):
    if theme not in AVAILABLE_THEMES:
        theme = "macos-new.css"
    os.makedirs(os.path.dirname(THEME_FILE), exist_ok=True)
    with open(THEME_FILE, "w", encoding="utf-8") as f:
        json.dump({"theme": theme}, f)

def get_current_theme():
    saved = get_saved_theme()
    if saved:
        return saved
    return get_theme_by_time()

if __name__ == "__main__":
    print(f"Тема по времени: {get_theme_by_time()}")
    print(f"Сохранённая тема: {get_saved_theme()}")
    print(f"Итоговая тема: {get_current_theme()}")
