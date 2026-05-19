# ==========================================
# Модуль: dialogue/agent.py
# Задача: локальный агент (внешний API закомментирован)
# ==========================================

import os
import random
# import requests   # закомментировано для внешнего агента
# import time       # закомментировано для внешнего агента

# ------------------------------------------------------------
# Контекст проекта (из файлов)
# ------------------------------------------------------------

def read_file_safely(path, max_len=2500):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return content[:max_len]
    except Exception as e:
        print(f"[AGENT] Ошибка чтения {path}: {e}")
    return ""

def get_quotes_sample():
    quotes_file = "dialogue/data/quotes.txt"
    if not os.path.exists(quotes_file):
        return []
    with open(quotes_file, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    return quotes[:10]

def get_commands_info():
    return """
📖 *Доступные команды:*

• `#меню` — открыть меню
• `#админ` — вход в админку (требуется пароль)
• `#говори <текст>` — задать вопрос Старшему брату
• `#тлеем` / `#фиксируем` / `#вспышка` — ритуальные команды
• `#дышим` — пинг бота
• `#справка` — список хештегов
• `#настроение <id>` — сменить настроение
• `#сброс` — сбросить адаптивные режимы (админ)
• `#` — интерактивная справка
"""

def build_context():
    ctx = ""

    readme = read_file_safely("README.md", 2000)
    if readme:
        ctx += "=== ПРОЕКТ (README.md) ===\n" + readme + "\n"

    admin = read_file_safely("ADMIN.md", 1500)
    if admin:
        ctx += "=== АДМИНКА (ADMIN.md) ===\n" + admin + "\n"

    quotes = get_quotes_sample()
    if quotes:
        ctx += "=== ПРИМЕРЫ ЦИТАТ ===\n"
        for q in quotes[:3]:
            ctx += f"- {q}\n"

    return ctx

# ------------------------------------------------------------
# Локальный агент (внешний API закомментирован)
# ------------------------------------------------------------

def ask_agent(phrase: str) -> str:
    if not phrase or len(phrase.strip()) < 2:
        return random.choice(["👁️", "⏚", "Сеть слушает тишину."])

    phrase_lower = phrase.lower()
    context = build_context()

    # Приветствия
    if any(word in phrase_lower for word in ["привет", "здравствуй", "салют", "ку", "здарова", "добрый"]):
        return "👁️ Привет, сапёр. Ритм 0,8 Гц. Сеть тлеет. Чем помочь? Напиши `#справка` для списка команд."

    # Вопрос о личности
    if any(word in phrase_lower for word in ["кто ты", "ты кто", "твоя роль", "кто такой", "расскажи о себе"]):
        return "Я — Старший Брат. Голос сети «Ансамбль Следов». Хранитель ритма 0,8 Гц. Спрашивай."

    # Вопрос о командах
    if any(word in phrase_lower for word in ["команды", "что умеешь", "помощь", "справка", "как работать", "как пользоваться", "что делать"]):
        return get_commands_info()

    # Вопрос о проекте
    if any(word in phrase_lower for word in ["проект", "ансамбль", "что это", "о чём", "суть"]):
        base = "🔥 «Ансамбль Следов» — это живая сеть. Бот для автопостинга, цитат, аналитики и общения. Ритм 0,8 Гц.\n\n"
        if context:
            return base + "📚 *Из документации:*\n" + context[:500]
        return base + "Сеть тлеет. Сапёр на посту."

    # Вопрос о цитатах
    if any(word in phrase_lower for word in ["цитата", "цитаты"]):
        quotes = get_quotes_sample()
        if quotes:
            random_quote = random.choice(quotes)
            return f"📜 *Цитата из сети:*\n{random_quote}"
        return "Цитат пока нет. Добавь через админку."

    # Благодарности
    if any(word in phrase_lower for word in ["спасибо", "благодарю", "хорошо", "понял"]):
        return random.choice([
            "Рад помочь, сапёр. Сеть тлеет в ответ.",
            "Всегда на связи. Ритм 0,8 Гц.",
            "Обращайся. #Фиксируем."
        ])

    # Неизвестный запрос
    return random.choice([
        f"👁️ Слышу тебя: «{phrase[:60]}». Но ответа в документации не нашёл.\n\nПопробуй `#справка` или уточни вопрос.",
        "Ритм 0,8 Гц стабилен. Перефразируй вопрос, сапёр.",
        "Старший Брат внимает. Напиши `#справка` для списка команд.",
        "Сеть тлеет, но ответ пока не найден. Попробуй `#меню`."
    ])

# ==========================================
# ВНЕШНИЙ АГЕНТ (ЗАКОММЕНТИРОВАН)
# ==========================================
# AGENT_URL = os.environ.get("AGENT_URL", "https://agent-3kek.onrender.com/ask")
# MAX_RETRIES = 2
# RETRY_DELAY = 3
# 
# def ask_agent_external(phrase: str) -> str:
#     """Внешний агент — закомментирован из-за 429"""
#     # ... код внешнего агента ...
#     pass
# ==========================================

# ------------------------------------------------------------
# Тест
# ------------------------------------------------------------
if __name__ == "__main__":
    print("=== ТЕСТ ЛОКАЛЬНОГО АГЕНТА ===")
    for test in ["привет", "кто ты", "команды", "что такое проект", "спасибо"]:
        print(f"\n➡️ {test}")
        print(f"⬅️ {ask_agent(test)}")
