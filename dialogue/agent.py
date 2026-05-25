# ==========================================
# Файл: dialogue/agent.py
# Справка: README.md → Агент / #говори
# Задача: лёгкий агент для Yandex GPT с эволюцией и памятью
# Комментарий: всё тяжёлое — во внешних модулях (journal, settings, memory, rules)
#              Добавлен механизм «осадка» для самообучения
# Зависит от: requests, os, json, debug_utils
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
RULES_FILE = "agent_data/rules.json"

# ==========================================
# ЗАГРУЗКА ПРАВИЛ (для применения)
# ==========================================
def load_rules():
    """Загружает правила эволюции из rules.json"""
    if not os.path.exists(RULES_FILE):
        return []
    try:
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("rules", [])
    except Exception as e:
        debug_log("AGENT", f"Ошибка загрузки правил: {e}", "WARNING")
        return []

def apply_rules(prompt, answer):
    """Применяет правила к ответу (модифицирует стиль, темп и т.д.)"""
    rules = load_rules()
    modified = answer
    for rule in rules:
        if not rule.get("enabled", True):
            continue
        condition = rule.get("condition", "")
        action = rule.get("action", "")
        
        # Простая проверка условия (можно расширить)
        if any(word in prompt.lower() for word in condition.lower().split()):
            debug_log("AGENT", f"Применено правило: {rule.get('id')} | {action[:50]}", "INFO")
            # Применяем действие (пока заглушка, можно расширить)
            if "ритм" in action.lower() or "темп" in action.lower():
                modified = modified + " [ритм 0,8 Гц]"
            elif "метафор" in action.lower():
                modified = "🌱 " + modified
    return modified

# ==========================================
# ЗАГРУЗКА НАСТРОЕК
# ==========================================
def _get_settings():
    from dialogue.agent_settings import get_agent_settings
    return get_agent_settings()

def _log_to_journal(text):
    from dialogue.agent_journal import log
    log(text)

def _add_sediment(prompt, answer, user_id):
    try:
        from evolve_agent import add_sediment
        return add_sediment(prompt, answer, user_id)
    except ImportError:
        debug_log("AGENT", "evolve_agent не загружен, осадок не сохранён", "WARNING")
        return False

def _load_context():
    try:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return None

def _get_mood_prompt(user_id):
    from dialogue.user_settings import get_user_mood, get_mood_prompt
    mood = get_user_mood(user_id) if user_id else "artist"
    return get_mood_prompt(mood)

# ==========================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==========================================
def ask_agent(prompt, user_id=None):
    """Основной метод агента — запрос к Yandex GPT с эволюцией"""
    if not YC_API_KEY or not YC_FOLDER_ID:
        return "⚙️ Агент не настроен. Проверь переменные окружения."

    settings = _get_settings()
    context = _load_context()
    mood_prompt = _get_mood_prompt(user_id)

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
        debug_log("AGENT", f"Запрос от user {user_id}: {prompt[:80]}...")
        r = requests.post(YANDEX_GPT_URL, headers={
            "Authorization": f"Api-Key {YC_API_KEY}",
            "Content-Type": "application/json"
        }, json=payload, timeout=30)
        r.raise_for_status()
        answer = r.json()['result']['alternatives'][0]['message']['text']
        
        # Применяем правила эволюции
        answer = apply_rules(prompt, answer)
        
        # Логируем в дневник
        _log_to_journal(f"User {user_id} | Q: {prompt[:80]} | A: {answer[:80]}")
        
        # Сохраняем осадок для эволюции
        _add_sediment(prompt, answer, user_id)
        
        return answer.strip()
    except Exception as e:
        debug_log("AGENT", f"Ошибка: {e}", "ERROR")
        _log_to_journal(f"Ошибка: {e}")
        return "🌙 Сеть шумит. Повтори позже."

def get_agent_status():
    """Возвращает статус агента для админки"""
    from dialogue.agent_settings import get_agent_settings
    from dialogue.agent_journal import get_journal_lines
    s = get_agent_settings()
    return {
        "temperature": s.get("temperature", 0.7),
        "max_tokens": s.get("max_tokens", 500),
        "journal_lines": get_journal_lines()
    }

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ АГЕНТА ===")
    test_prompt = "Что такое разлом?"
    print(f"Вопрос: {test_prompt}")
    print(f"Ответ: {ask_agent(test_prompt, user_id=123456)}")
