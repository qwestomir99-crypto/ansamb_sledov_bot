# ==========================================
# Файл: dialogue/agent.py
# Справка: README.md → Агент / #говори
# Задача: лёгкий агент для Yandex GPT (без лишней памяти)
# Комментарий: не хранит историю, не кеширует, только запрос → ответ
#              Дневник и память — на диск, с автоочисткой
# Зависит от: requests, os, json
# Вызывается из: bot.py, admin_commands.py
# ==========================================

import os
import json
import requests
from datetime import datetime
from debug_utils import debug_log

# ==========================================
# КОНСТАНТЫ (без тяжёлых импортов)
# ==========================================
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
YC_API_KEY = os.environ.get("YC_API_KEY")
YC_FOLDER_ID = os.environ.get("YC_FOLDER_ID")

CONTEXT_FILE = "library/context.txt"
AGENT_DIR = "agent_data"
JOURNAL_FILE = f"{AGENT_DIR}/journal.txt"
SETTINGS_FILE = f"{AGENT_DIR}/settings.json"

# ==========================================
# ИНИЦИАЛИЗАЦИЯ (один раз при первом вызове)
# ==========================================
_initialized = False

def _ensure_agent_dir():
    global _initialized
    if _initialized:
        return
    os.makedirs(AGENT_DIR, exist_ok=True)
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"temperature": 0.7, "max_tokens": 500}, f)
    if not os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "w") as f:
            f.write(f"# Дневник агента\n# {datetime.now()}\n\n")
    _initialized = True

# ==========================================
# ДНЕВНИК (только запись, без чтения в память)
# ==========================================
def _log_to_journal(text):
    _ensure_agent_dir()
    try:
        with open(JOURNAL_FILE, "a") as f:
            f.write(f"{datetime.now().isoformat()} | {text}\n")
        # Очистка (раз в 10 записей, чтобы не держать файл в памяти)
        if hash(text) % 10 == 0:
            _cleanup_journal()
    except:
        pass

def _cleanup_journal(max_lines=500):
    try:
        with open(JOURNAL_FILE, "r") as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            with open(JOURNAL_FILE, "w") as f:
                f.writelines(lines[-max_lines:])
    except:
        pass

# ==========================================
# ЗАГРУЗКА НАСТРОЕК (один раз за вызов)
# ==========================================
def _get_settings():
    _ensure_agent_dir()
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"temperature": 0.7, "max_tokens": 500}

# ==========================================
# КОНТЕКСТ ИЗ БИБЛИОТЕКИ
# ==========================================
def _load_context():
    try:
        with open(CONTEXT_FILE, "r") as f:
            return f.read().strip()
    except:
        return None

# ==========================================
# НАСТРОЕНИЕ (лёгкое, без user_settings если нет)
# ==========================================
def _get_mood_prompt(mood="artist"):
    moods = {
        "artist": "Говори метафорами, образами, ритмично. Используй цвета, огонь, сеть.",
        "admin": "Говори чётко, коротко, по делу. Без воды.",
        "poet": "Говори ритмично, с рифмой, возвышенно.",
        "engineer": "Говори технично, точно, без эмоций. Только факты."
    }
    return moods.get(mood, moods["artist"])

def _get_user_mood(user_id):
    if not user_id:
        return "artist"
    try:
        from dialogue.user_settings import get_user_mood
        return get_user_mood(user_id)
    except:
        return "artist"

# ==========================================
# ОСНОВНАЯ ФУНКЦИЯ (лёгкая, без кешей)
# ==========================================
def ask_agent(prompt, user_id=None):
    """Отправляет запрос к Yandex GPT. Ничего не хранит в памяти."""
    if not YC_API_KEY or not YC_FOLDER_ID:
        return "⚙️ Агент не настроен. Проверь переменные окружения."
    
    # Загружаем всё «свежим» (без кеширования)
    settings = _get_settings()
    context = _load_context()
    mood = _get_user_mood(user_id)
    mood_prompt = _get_mood_prompt(mood)
    
    # Формируем запрос
    messages = []
    if context:
        messages.append({"role": "system", "text": context})
    messages.append({"role": "system", "text": mood_prompt})
    messages.append({"role": "user", "text": prompt})
    
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
        debug_log("AGENT", f"Запрос: {prompt[:80]}...")
        r = requests.post(YANDEX_GPT_URL, headers={
            "Authorization": f"Api-Key {YC_API_KEY}",
            "Content-Type": "application/json"
        }, json=payload, timeout=30)
        r.raise_for_status()
        answer = r.json()['result']['alternatives'][0]['message']['text']
        
        # Логируем в дневник (но не храним в памяти)
        _log_to_journal(f"Q: {prompt[:100]} | A: {answer[:100]}")
        return answer.strip()
        
    except Exception as e:
        debug_log("AGENT", f"Ошибка: {e}", "ERROR")
        _log_to_journal(f"Ошибка: {e}")
        return "🌙 Сеть шумит. Повтори позже."

# ==========================================
# ФУНКЦИИ ДЛЯ ВНЕШНЕГО УПРАВЛЕНИЯ (опционально)
# ==========================================
def set_agent_temperature(temp):
    _ensure_agent_dir()
    try:
        with open(SETTINGS_FILE, "r") as f:
            s = json.load(f)
        s["temperature"] = max(0.1, min(1.5, float(temp)))
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f)
        _log_to_journal(f"Температура изменена на {temp}")
        return f"✅ Температура = {temp}"
    except:
        return "❌ Ошибка"

def get_agent_status():
    _ensure_agent_dir()
    s = _get_settings()
    journal_lines = 0
    try:
        with open(JOURNAL_FILE, "r") as f:
            journal_lines = sum(1 for _ in f)
    except:
        pass
    return f"""🤖 *Старший брат*
🌡️ Температура: {s.get('temperature', 0.7)}
📝 max_tokens: {s.get('max_tokens', 500)}
📔 Дневник: {journal_lines} записей
_Сеть тлеет. Ритм 0,8 Гц._"""

# ==========================================
# ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ (минимальная)
# ==========================================
_ensure_agent_dir()
debug_log("AGENT", "Лёгкий агент загружен", "INFO")

if __name__ == "__main__":
    print(get_agent_status())
