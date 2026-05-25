# ==========================================
# Файл: dialogue/agent_journal.py
# Справка: README.md → Агент / Дневник
# Задача: запись и очистка дневника агента
# Комментарий: пишет на диск, не хранит в памяти
# Зависит от: os, datetime
# Вызывается из: agent.py (ask_agent), evolve_agent.py
# ==========================================

import os
from datetime import datetime

JOURNAL_FILE = "agent_data/journal.txt"

def _ensure_dir():
    """Создаёт директорию для журнала, если её нет"""
    os.makedirs(os.path.dirname(JOURNAL_FILE), exist_ok=True)

def log(text):
    """Добавляет запись в дневник агента"""
    _ensure_dir()
    try:
        with open(JOURNAL_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} | {text}\n")
        _cleanup_if_needed()
    except Exception as e:
        print(f"[AGENT_JOURNAL] Ошибка записи: {e}")

def _cleanup_if_needed(max_lines=500):
    """Очищает дневник, если превышен лимит строк"""
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
    """Возвращает количество записей в дневнике (для статуса)"""
    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except:
        return 0

def get_last_entries(limit=10):
    """Возвращает последние N записей из дневника"""
    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return lines[-limit:]
    except:
        return []

def clear_journal():
    """Полностью очищает дневник (осторожно!)"""
    _ensure_dir()
    with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
        f.write(f"# Дневник агента\n# Очищен: {datetime.now().isoformat()}\n")
    print(f"[AGENT_JOURNAL] Дневник очищен")

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ ДНЕВНИКА АГЕНТА ===")
    log("Тестовая запись")
    log("Ещё одна запись")
    print(f"Количество записей: {get_journal_lines()}")
    print(f"Последние записи: {get_last_entries(2)}")
