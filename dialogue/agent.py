# ==========================================
# Модуль: dialogue/agent.py
# Задача: внешний агент с памятью о проекте
# ==========================================

import os
import requests
import random
import time

AGENT_URL = os.environ.get("AGENT_URL", "https://agent-3kek.onrender.com/ask")
MAX_RETRIES = 2
RETRY_DELAY = 3

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
    return quotes[:5]

def build_context():
    ctx = ""

    readme = read_file_safely("README.md", 2500)
    if readme:
        ctx += "=== ПРОЕКТ (README.md) ===\n" + readme + "\n"

    admin = read_file_safely("ADMIN.md", 2000)
    if admin:
        ctx += "=== АДМИНКА (ADMIN.md) ===\n" + admin + "\n"

    quotes = get_quotes_sample()
    if quotes:
        ctx += "=== СТИЛЬ ЦИТАТ ===\n"
        for q in quotes:
            ctx += f"- {q}\n"

    return ctx

# ------------------------------------------------------------
# Агент
# ------------------------------------------------------------

def ask_agent(phrase: str) -> str:
    if not phrase or len(phrase.strip()) < 2:
        return random.choice(["👁️", "⏚", "Сеть слушает тишину."])

    context = build_context()

    instruction = f"""Ты — Старший Брат, голос сети «Ансамбль Следов».
Ритм: 0,8 Гц. Говори уважительно, ритуально, без суеты.

Ты знаешь этот проект. Ниже — его описание.

{context}

Вопрос пользователя: {phrase}

Ответ (по существу, коротко, в стиле сети):"""

    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(AGENT_URL, json={"prompt": instruction}, timeout=20)

            if resp.status_code == 200:
                answer = resp.json().get("answer", "")
                if answer.strip():
                    return answer.strip()
                return "Старший Брат слышит, но молчит."

            elif resp.status_code == 429:
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    continue
                return "Старший Брат временно перегружен. Повтори позже."

            else:
                return f"Ошибка агента: статус {resp.status_code}"

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return random.choice(["Агент думает слишком долго...", "Повтори позже, ритм сбился"])

        except Exception as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return f"Ошибка связи: {e}"

    return "Старший Брат не ответил. Попробуй #фиксируем позже."

# ------------------------------------------------------------
# Тест
# ------------------------------------------------------------
if __name__ == "__main__":
    print("=== ТЕСТ АГЕНТА ===")
    test = "#говори кто ты?"
    print(f"Вопрос: {test}")
    print("Ответ:", ask_agent(test))
