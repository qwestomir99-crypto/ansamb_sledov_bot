# ==========================================
# Файл: dialogue/user_settings.py
# Справка: README.md → Настройки пользователя
# Задача: сохранение и управление настройками пользователей (настроение)
# Комментарий: поддерживает выбор настроения (художник, администратор, поэт, инженер)
#              Сохраняет настройки в файл dialogue/data/user_settings.json
# Зависит от: json, os
# Вызывается из: bot.py, admin_commands.py, callbacks.py, agent.py
# ==========================================

import os
import json
from debug_utils import debug_log

# ==========================================
# 1. ПУТИ К ФАЙЛАМ
# ==========================================
USER_SETTINGS_FILE = "dialogue/data/user_settings.json"

# ==========================================
# 2. СЛОВАРЬ НАСТРОЕНИЙ
# ==========================================
MOODS = {
    "artist": {
        "name": "Художник",
        "emoji": "🎨",
        "description": "Метафоры, образы, ритмичная речь"
    },
    "admin": {
        "name": "Администратор",
        "emoji": "📋",
        "description": "Чётко, структурированно, по делу"
    },
    "poet": {
        "name": "Поэт",
        "emoji": "🎭",
        "description": "Лирично, возвышенно, с рифмой"
    },
    "engineer": {
        "name": "Инженер",
        "emoji": "🔧",
        "description": "Технично, по делу, без эмоций"
    }
}

# ==========================================
# 3. SYSTEM PROMPTS ДЛЯ АГЕНТА
# ==========================================
MOOD_PROMPTS = {
    "artist": "Ты — художник-анархист. Говори метафорами, образами, ритмично. Используй цвета, формы, огонь, сеть, тление.",
    "admin": "Ты — строгий администратор. Говори чётко, коротко, структурированно. По делу, без воды.",
    "poet": "Ты — поэт. Говори ритмично, с рифмой, возвышенно. Используй образы и эмоции.",
    "engineer": "Ты — инженер. Говори технично, точно, без лишних эмоций. Только факты и логика."
}

# ==========================================
# 4. ЗАГРУЗКА И СОХРАНЕНИЕ НАСТРОЕК
# ==========================================
def load_user_settings():
    """Загружает настройки всех пользователей из файла"""
    if not os.path.exists(USER_SETTINGS_FILE):
        return {}
    try:
        with open(USER_SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        debug_log("USER_SETTINGS", f"Ошибка загрузки настроек: {e}", "ERROR")
        return {}

def save_user_settings(settings):
    """Сохраняет настройки пользователей в файл"""
    os.makedirs(os.path.dirname(USER_SETTINGS_FILE), exist_ok=True)
    try:
        with open(USER_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        debug_log("USER_SETTINGS", f"Ошибка сохранения настроек: {e}", "ERROR")

# ==========================================
# 5. ПОЛУЧЕНИЕ И УСТАНОВКА НАСТРОЕНИЯ
# ==========================================
def get_user_mood(user_id):
    """Возвращает текущее настроение пользователя (по умолчанию 'artist')"""
    settings = load_user_settings()
    user_id_str = str(user_id)
    mood = settings.get(user_id_str, {}).get("mood", "artist")
    if mood not in MOODS:
        mood = "artist"
    return mood

def set_user_mood(user_id, mood):
    """Устанавливает настроение пользователя"""
    if mood not in MOODS:
        debug_log("USER_SETTINGS", f"Неизвестное настроение: {mood}", "WARNING")
        return False
    
    settings = load_user_settings()
    user_id_str = str(user_id)
    if user_id_str not in settings:
        settings[user_id_str] = {}
    settings[user_id_str]["mood"] = mood
    save_user_settings(settings)
    debug_log("USER_SETTINGS", f"Пользователь {user_id} установил настроение: {mood}", "INFO")
    return True

def get_user_mood_name(user_id):
    """Возвращает название настроения пользователя на русском"""
    mood = get_user_mood(user_id)
    mood_names = {
        'artist': 'Художник',
        'admin': 'Администратор',
        'poet': 'Поэт',
        'engineer': 'Инженер'
    }
    return mood_names.get(mood, 'Художник')

def get_mood_info(mood):
    """Возвращает информацию о настроении"""
    return MOODS.get(mood, MOODS["artist"])

def get_mood_prompt(mood):
    """Возвращает system prompt для агента на основе настроения"""
    return MOOD_PROMPTS.get(mood, MOOD_PROMPTS["artist"])

# ==========================================
# 6. КЛАВИАТУРЫ ДЛЯ ВЫБОРА НАСТРОЕНИЯ
# ==========================================
def get_moods_keyboard(with_back=True):
    """Возвращает клавиатуру для выбора настроения"""
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    for mood_id, mood_data in MOODS.items():
        keyboard.add(InlineKeyboardButton(
            f"{mood_data['emoji']} {mood_data['name']}",
            callback_data=f"set_mood_{mood_id}"
        ))
    
    if with_back:
        keyboard.add(InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_admin"))
    
    keyboard.add(InlineKeyboardButton("❌ Закрыть", callback_data="admin_logout"))
    
    return keyboard

# ==========================================
# 7. ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ USER_SETTINGS ===")
    print(f"Доступные настроения: {list(MOODS.keys())}")
    test_user = 123456
    print(f"Текущее настроение: {get_user_mood(test_user)}")
    set_user_mood(test_user, "poet")
    print(f"Новое настроение: {get_user_mood(test_user)}")
    print(f"System prompt: {get_mood_prompt('artist')[:80]}...")
