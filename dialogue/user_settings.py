# ==========================================
# Модуль: dialogue/user_settings.py
# Справка: README.md → Настройки пользователей
# Задача: хранение персональных настроений и стилей
# Комментарий: каждый пользователь может выбрать своё настроение, ритм 0,8 Гц остаётся общим
# Зависит от: config.json
# Вызывается из: handlers.py, quotes.py
# ==========================================

import os
import json
import time

USER_SETTINGS_FILE = "dialogue/data/user_settings.json"

# Доступные настроения с их параметрами
MOODS = {
    "сапёр": {
        "name": "Сапёр",
        "emoji": "🛡️",
        "quotes_interval": 60,
        "publisher_interval": 120,
        "tags": ["#сапёр", "#наблюдение"],
        "style": "факты, логи, наблюдения"
    },
    "художник": {
        "name": "Художник",
        "emoji": "🎨",
        "quotes_interval": 30,
        "publisher_interval": 60,
        "tags": ["#искусство", "#образы"],
        "style": "образы, метафоры, визуальные цитаты"
    },
    "поэт": {
        "name": "Поэт",
        "emoji": "📜",
        "quotes_interval": 120,
        "publisher_interval": 240,
        "tags": ["#поэзия", "#тишина"],
        "style": "рифмы, тишина, глубокие цитаты"
    },
    "админ": {
        "name": "Админ",
        "emoji": "🛡️",
        "quotes_interval": 15,
        "publisher_interval": 30,
        "tags": ["#админ", "#управление"],
        "style": "команды, сводки, диагностика"
    },
    "наблюдатель": {
        "name": "Наблюдатель",
        "emoji": "👁️",
        "quotes_interval": 90,
        "publisher_interval": 180,
        "tags": ["#наблюдение", #тишина"],
        "style": "тихое наблюдение, минимум слов"
    },
    "философ": {
        "name": "Философ",
        "emoji": "🌌",
        "quotes_interval": 45,
        "publisher_interval": 90,
        "tags": ["#философия", "#смысл"],
        "style": "глубокие вопросы, рефлексия"
    }
}

def load_user_settings():
    """Загружает настройки всех пользователей"""
    if not os.path.exists(USER_SETTINGS_FILE):
        return {}
    with open(USER_SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_settings(settings):
    """Сохраняет настройки пользователей"""
    os.makedirs(os.path.dirname(USER_SETTINGS_FILE), exist_ok=True)
    with open(USER_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

def get_user_mood(user_id):
    """Возвращает настроение пользователя (по умолчанию «сапёр»)"""
    settings = load_user_settings()
    user_id_str = str(user_id)
    if user_id_str in settings:
        mood = settings[user_id_str].get("mood", "сапёр")
        if mood in MOODS:
            return mood
    return "сапёр"

def set_user_mood(user_id, mood):
    """Устанавливает настроение пользователя"""
    if mood not in MOODS:
        return False
    
    settings = load_user_settings()
    user_id_str = str(user_id)
    if user_id_str not in settings:
        settings[user_id_str] = {}
    
    settings[user_id_str]["mood"] = mood
    settings[user_id_str]["updated_at"] = time.time()
    save_user_settings(settings)
    return True

def get_user_quotes_interval(user_id, base_interval):
    """Возвращает персональный интервал цитат для пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    return mood_config.get("quotes_interval", base_interval)

def get_user_publisher_interval(user_id, base_interval):
    """Возвращает персональный интервал публикаций для пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    return mood_config.get("publisher_interval", base_interval)

def get_user_tags(user_id):
    """Возвращает персональные теги для пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    return mood_config.get("tags", [])

def get_user_style(user_id):
    """Возвращает стиль ответов для пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    return mood_config.get("style", "факты, логи")

def get_user_emoji(user_id):
    """Возвращает эмодзи настроения пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    return mood_config.get("emoji", "🛡️")

def get_available_moods():
    """Возвращает список доступных настроений с описанием"""
    result = []
    for mood, config in MOODS.items():
        result.append({
            "id": mood,
            "name": config["name"],
            "emoji": config["emoji"],
            "style": config["style"]
        })
    return result
