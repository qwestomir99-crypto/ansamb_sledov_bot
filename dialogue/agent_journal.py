# ==========================================
# Файл: dialogue/agent_journal.py
# Справка: README.md → Агент / Дневник
# Задача: запись и очистка дневника агента
# Комментарий: хранится в library/agent_journal.md
# Зависит от: os, datetime
# Вызывается из: agent.py (ask_agent), evolve_agent.py
# ==========================================

import os
from datetime import datetime

JOURNAL_FILE = "library/agent_journal.md"

def _ensure_dir():
    os.makedirs(os.path.dirname(JOURNAL_FILE), exist_ok=True)

def log(text):
    _ensure_dir()
    try:
        with open(JOURNAL_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} | {text}\n")
        _cleanup_if_needed()
    except Exception as e:
        print(f"[AGENT_JOURNAL] Ошибка записи: {e}")

def _cleanup_if_needed(max_lines=500):
    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines[-max_lines:])
            print(f"[AGENT_JOURNAL] Дневник очищен, осталось {max_lines} строк")
    except Exception as e:
        print(f"[AGENT_JOURNAL] Ошибка очистки: {e}")

def get_journal_lines():
    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except:
        return 0

def get_last_entries(limit=10):
    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return lines[-limit:]
    except:
        return []

def clear_journal():
    _ensure_dir()
    with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
        f.write(f"# Дневник агента\n# Очищен: {datetime.now().isoformat()}\n")
    print(f"[AGENT_JOURNAL] Дневник очищен")

if __name__ == "__main__":
    print("=== ТЕСТ ДНЕВНИКА АГЕНТА ===")
    log("Тестовая запись")
    log("Ещё одна запись")
    print(f"Количество записей: {get_journal_lines()}")
    print(f"Последние записи: {get_last_entries(2)}")
