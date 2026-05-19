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
        "style": "факты, логи, наблюдения",
        "description": "Холодный расчёт, факты, диагностика"
    },
    "художник": {
        "name": "Художник",
        "emoji": "🎨",
        "quotes_interval": 30,
        "publisher_interval": 60,
        "tags": ["#искусство", "#образы"],
        "style": "образы, метафоры, визуальные цитаты",
        "description": "Образы, метафоры, визуальные цитаты"
    },
    "поэт": {
        "name": "Поэт",
        "emoji": "📜",
        "quotes_interval": 120,
        "publisher_interval": 240,
        "tags": ["#поэзия", "#тишина"],
        "style": "рифмы, тишина, глубокие цитаты",
        "description": "Рифмы, тишина, глубокие цитаты"
    },
    "админ": {
        "name": "Админ",
        "emoji": "🛠️",
        "quotes_interval": 15,
        "publisher_interval": 30,
        "tags": ["#админ", "#управление"],
        "style": "команды, сводки, диагностика",
        "description": "Команды, сводки, диагностика (только для админов)"
    },
    "наблюдатель": {
        "name": "Наблюдатель",
        "emoji": "👁️",
        "quotes_interval": 90,
        "publisher_interval": 180,
        "tags": ["#наблюдение", "#тишина"],
        "style": "тихое наблюдение, минимум слов",
        "description": "Тихое наблюдение, минимум слов"
    },
    "философ": {
        "name": "Философ",
        "emoji": "🌌",
        "quotes_interval": 45,
        "publisher_interval": 90,
        "tags": ["#философия", "#смысл"],
        "style": "глубокие вопросы, рефлексия",
        "description": "Глубокие вопросы, рефлексия"
    }
}

def load_user_settings():
    """Загружает настройки всех пользователей"""
    if not os.path.exists(USER_SETTINGS_FILE):
        return {}
    try:
        with open(USER_SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[USER_SETTINGS] Ошибка загрузки: {e}")
        return {}

def save_user_settings(settings):
    """Сохраняет настройки пользователей"""
    try:
        os.makedirs(os.path.dirname(USER_SETTINGS_FILE), exist_ok=True)
        with open(USER_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[USER_SETTINGS] Ошибка сохранения: {e}")
        return False

def get_user_settings(user_id):
    """Возвращает настройки конкретного пользователя"""
    settings = load_user_settings()
    user_id_str = str(user_id)
    if user_id_str in settings:
        return settings[user_id_str]
    return {"mood": "сапёр", "updated_at": 0}

def get_user_mood(user_id):
    """Возвращает настроение пользователя (по умолчанию «сапёр»)"""
    user_settings = get_user_settings(user_id)
    mood = user_settings.get("mood", "сапёр")
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
    settings[user_id_str]["updated_at_readable"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    save_user_settings(settings)
    return True

def get_user_quotes_interval(user_id, base_interval=None):
    """Возвращает персональный интервал цитат для пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    return mood_config.get("quotes_interval", base_interval or 60)

def get_user_publisher_interval(user_id, base_interval=None):
    """Возвращает персональный интервал публикаций для пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    return mood_config.get("publisher_interval", base_interval or 120)

def get_user_tags(user_id):
    """Возвращает персональные теги для пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    return mood_config.get("tags", [])

def get_user_style(user_id):
    """Возвращает стиль ответов для пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    return mood_config.get("style", "факты, логи, наблюдения")

def get_user_emoji(user_id):
    """Возвращает эмодзи настроения пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    return mood_config.get("emoji", "🛡️")

def get_user_description(user_id):
    """Возвращает описание настроения пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    return mood_config.get("description", "Наблюдение и фиксация")

def get_available_moods():
    """Возвращает список доступных настроений с описанием"""
    result = []
    for mood, config in MOODS.items():
        result.append({
            "id": mood,
            "name": config["name"],
            "emoji": config["emoji"],
            "style": config["style"],
            "description": config.get("description", config["style"])
        })
    return result

def get_user_mood_info(user_id):
    """Возвращает полную информацию о настроении пользователя"""
    mood = get_user_mood(user_id)
    mood_config = MOODS.get(mood, MOODS["сапёр"])
    user_settings = get_user_settings(user_id)
    
    return {
        "user_id": user_id,
        "mood": mood,
        "mood_name": mood_config["name"],
        "emoji": mood_config["emoji"],
        "style": mood_config["style"],
        "quotes_interval": mood_config["quotes_interval"],
        "publisher_interval": mood_config["publisher_interval"],
        "tags": mood_config["tags"],
        "updated_at": user_settings.get("updated_at", 0),
        "updated_at_readable": user_settings.get("updated_at_readable", "никогда")
    }

def reset_user_mood(user_id):
    """Сбрасывает настроение пользователя к «сапёр»"""
    return set_user_mood(user_id, "сапёр")

def get_all_users_moods():
    """Возвращает словарь {user_id: mood} для всех пользователей"""
    settings = load_user_settings()
    result = {}
    for user_id, user_data in settings.items():
        result[user_id] = user_data.get("mood", "сапёр")
    return result

# Для совместимости с datetime
from datetime import datetime
