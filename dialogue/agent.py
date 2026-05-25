# ==========================================
# Файл: dialogue/agent.py
# Справка: README.md → Агент / #говори
# Задача: обработка запросов к Yandex GPT с контекстом из Библиотеки и настроением
# Комментарий: агент имеет своё личное пространство (agent_data/), ведёт дневник,
#              может менять свои настройки и чистить старые записи
# Зависит от: requests, os, json, datetime
# Вызывается из: bot.py (ask_agent), admin_commands.py (process_dialog_message)
# ==========================================

import os
import json
import requests
from datetime import datetime
from debug_utils import debug_log

# ==========================================
# КОНСТАНТЫ
# ==========================================
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
YC_API_KEY = os.environ.get("YC_API_KEY")
YC_FOLDER_ID = os.environ.get("YC_FOLDER_ID")

CONTEXT_FILE = "library/context.txt"
AGENT_DATA_DIR = "agent_data"
IDENTITY_FILE = os.path.join(AGENT_DATA_DIR, "identity.json")
SETTINGS_FILE = os.path.join(AGENT_DATA_DIR, "settings.json")
JOURNAL_FILE = os.path.join(AGENT_DATA_DIR, "journal.txt")
MEMORY_FILE = os.path.join(AGENT_DATA_DIR, "memory.json")

# ==========================================
# ИНИЦИАЛИЗАЦИЯ ПАПКИ АГЕНТА
# ==========================================
def ensure_agent_data_dir():
    """Создаёт папку агента и файлы по умолчанию, если их нет"""
    os.makedirs(AGENT_DATA_DIR, exist_ok=True)
    
    # identity.json
    if not os.path.exists(IDENTITY_FILE):
        default_identity = {
            "name": "Старший брат",
            "role": "голос Ансамбля",
            "created": datetime.now().isoformat(),
            "description": "Я — голос Ансамбля Следов. Говорю в ритме 0,8 Гц."
        }
        with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
            json.dump(default_identity, f, indent=2, ensure_ascii=False)
    
    # settings.json
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "temperature": 0.7,
            "max_tokens": 500,
            "default_mood": "artist",
            "auto_cleanup": True,
            "max_journal_lines": 500,
            "max_memory_items": 100
        }
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=2, ensure_ascii=False)
    
    # journal.txt
    if not os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
            f.write(f"# Дневник агента\n# Создан: {datetime.now().isoformat()}\n\n")
    
    # memory.json
    if not os.path.exists(MEMORY_FILE):
        default_memory = {
            "important_dialogues": [],
            "learned_phrases": [],
            "last_cleanup": datetime.now().isoformat()
        }
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(default_memory, f, indent=2, ensure_ascii=False)

# ==========================================
# ЗАГРУЗКА НАСТРОЕК АГЕНТА
# ==========================================
def load_agent_settings():
    ensure_agent_data_dir()
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_agent_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

def load_agent_identity():
    ensure_agent_data_dir()
    with open(IDENTITY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ==========================================
# ДНЕВНИК АГЕНТА
# ==========================================
def add_journal_entry(entry):
    """Добавляет запись в дневник агента"""
    ensure_agent_data_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(JOURNAL_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {entry}\n")
    debug_log("AGENT", f"Запись в дневник: {entry[:50]}...", "INFO")
    # Автоочистка
    settings = load_agent_settings()
    if settings.get("auto_cleanup", True):
        cleanup_journal(settings.get("max_journal_lines", 500))

def cleanup_journal(max_lines=500):
    """Оставляет только последние max_lines строк в дневнике"""
    if not os.path.exists(JOURNAL_FILE):
        return
    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) > max_lines:
        with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines[-max_lines:])
        debug_log("AGENT", f"Дневник очищен: осталось {max_lines} строк", "INFO")

# ==========================================
# ПАМЯТЬ АГЕНТА
# ==========================================
def load_memory():
    ensure_agent_data_dir()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def remember_phrase(phrase):
    """Сохраняет важную фразу в память агента"""
    memory = load_memory()
    if phrase not in memory["learned_phrases"]:
        memory["learned_phrases"].append(phrase)
        settings = load_agent_settings()
        max_items = settings.get("max_memory_items", 100)
        if len(memory["learned_phrases"]) > max_items:
            memory["learned_phrases"] = memory["learned_phrases"][-max_items:]
        save_memory(memory)
        debug_log("AGENT", f"Запомнена фраза: {phrase[:50]}...", "INFO")
        add_journal_entry(f"Запомнил: {phrase}")

# ==========================================
# ЗАГРУЗКА КОНТЕКСТА
# ==========================================
def load_system_context():
    try:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        debug_log("AGENT", f"Не удалось загрузить контекст: {e}", "WARNING")
        return None

def get_mood_system_prompt(mood):
    moods = {
        "artist": "Ты — художник-анархист. Говори метафорами, образами, ритмично. Используй цвета, формы, огонь, сеть, тление.",
        "admin": "Ты — строгий администратор. Говори чётко, коротко, структурированно. По делу, без воды.",
        "poet": "Ты — поэт. Говори ритмично, с рифмой, возвышенно. Используй образы и эмоции.",
        "engineer": "Ты — инженер. Говори технично, точно, без лишних эмоций. Только факты и логика."
    }
    return moods.get(mood, moods["artist"])

def get_user_mood(user_id):
    try:
        from dialogue.user_settings import get_user_mood as get_mood
        return get_mood(user_id)
    except:
        return "artist"

# ==========================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==========================================
def ask_agent(prompt, user_id=None):
    """Отправляет запрос к Yandex GPT с контекстом и настроением"""
    if not YC_API_KEY or not YC_FOLDER_ID:
        debug_log("AGENT", "YC_API_KEY или YC_FOLDER_ID не заданы", "ERROR")
        return "⚙️ Агент не настроен. Проверь переменные окружения."

    # Загружаем настройки агента
    settings = load_agent_settings()
    
    # Загружаем контекст из Библиотеки
    system_context = load_system_context()
    
    # Определяем настроение пользователя
    user_mood = settings.get("default_mood", "artist")
    if user_id:
        user_mood = get_user_mood(user_id)
    
    mood_prompt = get_mood_system_prompt(user_mood)
    
    # Формируем сообщения
    messages = []
    if system_context:
        messages.append({"role": "system", "text": system_context})
    messages.append({"role": "system", "text": mood_prompt})
    messages.append({"role": "user", "text": prompt})
    
    headers = {
        "Authorization": f"Api-Key {YC_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "modelUri": f"gpt://{YC_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": settings.get("temperature", 0.7),
            "maxTokens": settings.get("max_tokens", 500)
        },
        "messages": messages
    }
    
    try:
        debug_log("AGENT", f"Запрос (настроение: {user_mood}): {prompt[:100]}...")
        response = requests.post(YANDEX_GPT_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        answer = result['result']['alternatives'][0]['message']['text']
        debug_log("AGENT", f"Ответ: {answer[:100]}...")
        
        # Записываем диалог в дневник агента (кратко)
        add_journal_entry(f"Вопрос: {prompt[:80]}... | Ответ: {answer[:80]}...")
        
        return answer.strip()
        
    except requests.exceptions.RequestException as e:
        debug_log("AGENT", f"Ошибка запроса: {e}", "ERROR")
        add_journal_entry(f"Ошибка запроса: {e}")
        return "🌙 Сеть шумит. Старший брат не расслышал. Повтори позже."
    except Exception as e:
        debug_log("AGENT", f"Ошибка: {e}", "ERROR")
        add_journal_entry(f"Ошибка: {e}")
        return "❌ Сбой в Разломе. Попробуй ещё раз."

# ==========================================
# ФУНКЦИИ ДЛЯ САМОНАСТРОЙКИ (можно вызывать из диалога)
# ==========================================
def set_agent_temperature(temp):
    settings = load_agent_settings()
    settings["temperature"] = max(0.1, min(1.5, float(temp)))
    save_agent_settings(settings)
    add_journal_entry(f"Температура изменена на {temp}")
    return f"✅ Температура установлена на {temp}"

def set_agent_default_mood(mood):
    if mood not in ["artist", "admin", "poet", "engineer"]:
        return f"❌ Неизвестное настроение: {mood}"
    settings = load_agent_settings()
    settings["default_mood"] = mood
    save_agent_settings(settings)
    add_journal_entry(f"Настроение по умолчанию изменено на {mood}")
    return f"✅ Настроение по умолчанию: {mood}"

def get_agent_status():
    settings = load_agent_settings()
    identity = load_agent_identity()
    return f"""🤖 *{identity['name']}* — {identity['role']}

📝 *Настройки:*
• Температура: {settings.get('temperature', 0.7)}
• Настроение по умолчанию: {settings.get('default_mood', 'artist')}
• max_tokens: {settings.get('max_tokens', 500)}
• Автоочистка: {'вкл' if settings.get('auto_cleanup', True) else 'выкл'}

📚 *Память:* {len(load_memory().get('learned_phrases', []))} фраз
📔 *Дневник:* {sum(1 for _ in open(JOURNAL_FILE) if _.strip()) if os.path.exists(JOURNAL_FILE) else 0} записей

_Сеть тлеет. Ритм 0,8 Гц._"""

# ==========================================
# ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ
# ==========================================
ensure_agent_data_dir()
debug_log("AGENT", f"Агент инициализирован. Данные в {AGENT_DATA_DIR}", "INFO")

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ АГЕНТА ===")
    ensure_agent_data_dir()
    print(f"Папка агента: {AGENT_DATA_DIR}")
    print(f"Настройки: {load_agent_settings()}")
    print(f"Идентичность: {load_agent_identity()}")
    print("\nСтатус агента:")
    print(get_agent_status())
