# ==========================================
# Файл: dialogue/user_settings.py
# Справка: README.md → Настройки пользователя
# Задача: сохранение и управление настройками пользователей (настроение, режимы)
# Комментарий: поддерживает выбор настроения (художник, администратор, поэт, инженер)
#              Сохраняет настройки в файл dialogue/data/user_settings.json
# Зависит от: json, os
# Вызывается из: bot.py, admin_commands.py, callbacks.py
# ==========================================

import os
import json
from debug_utils import debug_log

# ==========================================
# 1. ПУТИ К ФАЙЛАМ
# ==========================================
USER_SETTINGS_FILE = "dialogue/data/user_settings.json"
MOODS_FILE = "dialogue/data/moods.json"

# ==========================================
# 2. СЛОВАРЬ НАСТРОЕНИЙ (по умолчанию)
# ==========================================
MOODS = {
    "artist": {
        "name": "Художник",
        "emoji": "🎨",
        "description": "Метафоры, образы, ритмичная речь",
        "system_prompt": "Ты — художник-анархист. Говори метафорами, образами, ритмично. Используй цвета, формы, огонь, сеть, тление."
    },
    "admin": {
        "name": "Администратор",
        "emoji": "📋",
        "description": "Чётко, структурированно, по делу",
        "system_prompt": "Ты — строгий администратор. Говори чётко, коротко, структурированно. По делу, без воды."
    },
    "poet": {
        "name": "Поэт",
        "emoji": "🎭",
        "description": "Лирично, возвышенно, с рифмой",
        "system_prompt": "Ты — поэт. Говори ритмично, с рифмой, возвышенно. Используй образы и эмоции."
    },
    "engineer": {
        "name": "Инженер",
        "emoji": "🔧",
        "description": "Технично, по делу, без эмоций",
        "system_prompt": "Ты — инженер. Говори технично, точно, без лишних эмоций. Только факты и логика."
    }
}

# ==========================================
# 3. ЗАГРУЗКА И СОХРАНЕНИЕ НАСТРОЕК
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
# 4. ПОЛУЧЕНИЕ И УСТАНОВКА НАСТРОЕНИЯ
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

def get_mood_info(mood):
    """Возвращает информацию о настроении"""
    return MOODS.get(mood, MOODS["artist"])

def get_mood_system_prompt(user_id):
    """Возвращает system prompt для агента на основе настроения пользователя"""
    mood = get_user_mood(user_id)
    return MOODS.get(mood, MOODS["artist"])["system_prompt"]

# ==========================================
# 5. КЛАВИАТУРЫ ДЛЯ ВЫБОРА НАСТРОЕНИЯ
# ==========================================
def get_moods_keyboard(with_back=True):
    """
    Возвращает клавиатуру для выбора настроения.
    - with_back=True: добавляет кнопку "◀️ Назад в меню"
    - всегда есть кнопка "❌ Закрыть" (выход из админки)
    """
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
# 6. ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ USER_SETTINGS ===")
    print(f"Доступные настроения: {list(MOODS.keys())}")
    
    # Тест установки
    test_user = 123456
    print(f"Текущее настроение: {get_user_mood(test_user)}")
    set_user_mood(test_user, "poet")
    print(f"Новое настроение: {get_user_mood(test_user)}")
    
    # Тест system prompt
    print(f"System prompt: {get_mood_system_prompt(test_user)[:100]}...")
