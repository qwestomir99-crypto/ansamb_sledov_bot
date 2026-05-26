# ==========================================
# Файл: dialogue/agent.py
# Справка: README.md → Агент / #говори
# Задача: лёгкий агент для Yandex GPT с персонажами и библиотекой
# Комментарий: весь контент — в library/, правила — в evolve_agent.py,
#              память — в agent_memory.py, журнал — в agent_journal.py,
#              настройки — в agent_settings.py.
#              agent.py — тонкий слой между запросом и библиотекой.
# Зависит от: requests, os, json, debug_utils, library/, evolve_agent, memory, journal, settings
# Вызывается из: bot.py (ask_agent), admin_commands.py (process_dialog_message)
# ==========================================

import os
import json
import requests
from datetime import datetime
from debug_utils import debug_log

# ==========================================
# ВНЕШНИЕ МОДУЛИ
# ==========================================
try:
    from dialogue.agent_settings import get_agent_settings
    from dialogue.agent_journal import log as log_to_journal
    from dialogue.agent_memory import remember_phrase, remember_dialogue, get_memory_stats
    from evolve_agent import add_sediment, apply_rules
    from dialogue.user_settings import get_user_mood, get_mood_prompt
except ImportError as e:
    debug_log("AGENT", f"Не удалось импортировать внешние модули: {e}", "ERROR")
    # Заглушки, чтобы не падало при отсутствии модулей
    def get_agent_settings(): return {}
    def log_to_journal(*args): pass
    def remember_phrase(*args): return False
    def remember_dialogue(*args): return False
    def get_memory_stats(): return {}
    def add_sediment(*args): return False
    def apply_rules(*args): return ""
    def get_user_mood(*args): return "artist"
    def get_mood_prompt(*args): return ""

# ==========================================
# КОНСТАНТЫ
# ==========================================
YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
YC_API_KEY = os.environ.get("YC_API_KEY")
YC_FOLDER_ID = os.environ.get("YC_FOLDER_ID")

CONTEXT_FILE = "library/context.txt"
LIBRARY_INDEX = "library/schema.json"
CHARACTERS_FILE = "library/characters.md"

# ==========================================
# ЗАГРУЗКА ПЕРСОНАЖЕЙ (из library/)
# ==========================================
def load_characters():
    """Загружает персонажей из schema.json (машиночитаемый индекс)"""
    if not os.path.exists(LIBRARY_INDEX):
        debug_log("AGENT", "schema.json не найден, персонажи не загружены", "WARNING")
        return {}
    try:
        with open(LIBRARY_INDEX, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("characters", {})
    except Exception as e:
        debug_log("AGENT", f"Ошибка загрузки персонажей: {e}", "ERROR")
        return {}

def detect_character(prompt):
    """Определяет персонажа по триггерам из schema.json"""
    characters = load_characters()
    if not characters:
        return None
    
    best_match = None
    max_hits = 0
    
    for char_id, char_data in characters.items():
        triggers = char_data.get("triggers", [])
        hits = sum(1 for t in triggers if t.lower() in prompt.lower())
        if hits > max_hits:
            max_hits = hits
            best_match = char_id
    
    if max_hits == 0:
        return None
    
    return characters.get(best_match, {})

# ==========================================
# ЗАГРУЗКА КОНТЕКСТА
# ==========================================
def load_context():
    try:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return None

# ==========================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==========================================
def ask_agent(prompt, user_id=None):
    """Основной метод агента — запрос к Yandex GPT с персонажами и библиотекой"""
    if not YC_API_KEY or not YC_FOLDER_ID:
        return "⚙️ Агент не настроен. Проверь переменные окружения."

    settings = get_agent_settings()
    context = load_context()
    
    # Определяем персонажа по контексту
    char = detect_character(prompt)
    char_name = char.get("name", "Агент") if char else "Агент"
    char_prompt = f"Ты — {char_name}. " + char.get("prompt", "") if char else ""
    
    # Загружаем настроение пользователя
    mood_prompt = get_mood_prompt(get_user_mood(user_id))

    messages = []
    if context:
        messages.append({"role": "system", "text": context})
    if char_prompt:
        messages.append({"role": "system", "text": char_prompt})
    if mood_prompt:
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
        debug_log("AGENT", f"Запрос от user {user_id} (персонаж: {char_name}): {prompt[:80]}...")
        r = requests.post(YANDEX_GPT_URL, headers={
            "Authorization": f"Api-Key {YC_API_KEY}",
            "Content-Type": "application/json"
        }, json=payload, timeout=30)
        r.raise_for_status()
        answer = r.json()['result']['alternatives'][0]['message']['text']
        
        # Применяем правила эволюции (из evolve_agent.py)
        answer = apply_rules(prompt, answer)
        
        # Логируем в дневник
        log_to_journal(f"User {user_id} | {char_name} | Q: {prompt[:80]} | A: {answer[:80]}")
        
        # Сохраняем осадок для эволюции
        add_sediment(prompt, answer, user_id)
        
        # Запоминаем важные фразы и диалоги (опционально)
        if len(prompt) > 20 and len(answer) > 20:
            remember_dialogue(prompt, answer, user_id)
        
        return answer.strip()
    except Exception as e:
        debug_log("AGENT", f"Ошибка: {e}", "ERROR")
        log_to_journal(f"Ошибка: {e}")
        return "🌙 Сеть шумит. Повтори позже."

def get_agent_status():
    """Возвращает статус агента для админки"""
    settings = get_agent_settings()
    journal_lines = 0
    try:
        from dialogue.agent_journal import get_journal_lines
        journal_lines = get_journal_lines()
    except ImportError:
        pass
    
    memory_stats = get_memory_stats()
    
    return {
        "temperature": settings.get("temperature", 0.7),
        "max_tokens": settings.get("max_tokens", 500),
        "journal_lines": journal_lines,
        "memory_phrases": memory_stats.get("phrases_count", 0),
        "memory_dialogues": memory_stats.get("dialogues_count", 0),
        "character": "auto-detected"
    }

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ АГЕНТА ===")
    test_prompt = "Что такое разлом?"
    print(f"Вопрос: {test_prompt}")
    print(f"Ответ: {ask_agent(test_prompt, user_id=123456)}")
    print("\nСтатус агента:")
    print(get_agent_status())
