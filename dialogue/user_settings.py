# ==========================================
# Файл: dialogue/user_settings.py
# Справка: README.md → Настройки пользователя
# Задача: сохранение и управление настройками пользователей (настроение)
# Комментарий: УПРОЩЁННАЯ ВЕРСИЯ — только базовые функции
# ==========================================

import os
import json
from debug_utils import debug_log

USER_SETTINGS_FILE = "dialogue/data/user_settings.json"

def load_user_settings():
    if not os.path.exists(USER_SETTINGS_FILE):
        return {}
    try:
        with open(USER_SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        debug_log("USER_SETTINGS", f"Ошибка загрузки: {e}", "ERROR")
        return {}

def save_user_settings(settings):
    os.makedirs(os.path.dirname(USER_SETTINGS_FILE), exist_ok=True)
    try:
        with open(USER_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        debug_log("USER_SETTINGS", f"Ошибка сохранения: {e}", "ERROR")

def get_user_mood(user_id):
    settings = load_user_settings()
    user_id_str = str(user_id)
    return settings.get(user_id_str, {}).get("mood", "artist")

def set_user_mood(user_id, mood):
    if mood not in ["artist", "admin", "poet", "engineer"]:
        return False
    settings = load_user_settings()
    user_id_str = str(user_id)
    if user_id_str not in settings:
        settings[user_id_str] = {}
    settings[user_id_str]["mood"] = mood
    save_user_settings(settings)
    debug_log("USER_SETTINGS", f"Пользователь {user_id} -> {mood}", "INFO")
    return True

def get_user_mood_name(user_id):
    mood = get_user_mood(user_id)
    names = {
        "artist": "Художник",
        "admin": "Администратор",
        "poet": "Поэт",
        "engineer": "Инженер"
    }
    return names.get(mood, "Художник")
