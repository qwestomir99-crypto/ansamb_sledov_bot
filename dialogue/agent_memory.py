# ==========================================
# Файл: dialogue/agent_memory.py
# Справка: README.md → Агент / Память
# Задача: хранение важных фраз и контекста (задел на будущее)
# Комментарий: опциональный модуль, не влияет на основную работу агента
#              Пока не используется, но память уже есть
# Зависит от: json, os
# Вызывается из: (пока не вызывается)
# ==========================================

import os
import json
from datetime import datetime
from debug_utils import debug_log

MEMORY_FILE = "agent_data/memory.json"

def _ensure_dir():
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)

def get_memory():
    """Загружает память агента"""
    _ensure_dir()
    if not os.path.exists(MEMORY_FILE):
        return {
            "learned_phrases": [],
            "important_dialogues": [],
            "last_cleanup": datetime.now().isoformat()
        }
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        debug_log("AGENT_MEMORY", f"Ошибка загрузки памяти: {e}", "ERROR")
        return {
            "learned_phrases": [],
            "important_dialogues": [],
            "last_cleanup": datetime.now().isoformat()
        }

def save_memory(memory):
    """Сохраняет память агента"""
    _ensure_dir()
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        debug_log("AGENT_MEMORY", f"Ошибка сохранения памяти: {e}", "ERROR")

def remember_phrase(phrase):
    """Сохраняет важную фразу в память агента"""
    memory = get_memory()
    if phrase not in memory["learned_phrases"]:
        memory["learned_phrases"].append(phrase)
        # Ограничиваем размер (не более 100 фраз)
        if len(memory["learned_phrases"]) > 100:
            memory["learned_phrases"] = memory["learned_phrases"][-100:]
        save_memory(memory)
        debug_log("AGENT_MEMORY", f"Запомнена фраза: {phrase[:50]}...", "INFO")
        return True
    return False

def forget_phrase(phrase):
    """Удаляет фразу из памяти"""
    memory = get_memory()
    if phrase in memory["learned_phrases"]:
        memory["learned_phrases"].remove(phrase)
        save_memory(memory)
        debug_log("AGENT_MEMORY", f"Фраза забыта: {phrase[:50]}...", "INFO")
        return True
    return False

def get_learned_phrases(limit=10):
    """Возвращает последние выученные фразы"""
    memory = get_memory()
    return memory.get("learned_phrases", [])[-limit:]

def remember_dialogue(question, answer):
    """Сохраняет важный диалог (вопрос-ответ)"""
    memory = get_memory()
    memory["important_dialogues"].append({
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    })
    # Ограничиваем размер (не более 50 диалогов)
    if len(memory["important_dialogues"]) > 50:
        memory["important_dialogues"] = memory["important_dialogues"][-50:]
    save_memory(memory)
    debug_log("AGENT_MEMORY", f"Диалог запомнен: {question[:50]}...", "INFO")

def cleanup_old_memory(days=30):
    """Удаляет старые диалоги из памяти"""
    memory = get_memory()
    cutoff = datetime.now().timestamp() - (days * 86400)
    new_dialogues = []
    for d in memory.get("important_dialogues", []):
        try:
            ts = datetime.fromisoformat(d["timestamp"]).timestamp()
            if ts > cutoff:
                new_dialogues.append(d)
        except:
            new_dialogues.append(d)
    memory["important_dialogues"] = new_dialogues
    memory["last_cleanup"] = datetime.now().isoformat()
    save_memory(memory)
    debug_log("AGENT_MEMORY", f"Память очищена (старше {days} дней)", "INFO")

def get_memory_stats():
    """Возвращает статистику памяти агента"""
    memory = get_memory()
    return {
        "phrases_count": len(memory.get("learned_phrases", [])),
        "dialogues_count": len(memory.get("important_dialogues", [])),
        "last_cleanup": memory.get("last_cleanup", "никогда")
    }

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ ПАМЯТИ АГЕНТА ===")
    print(f"Статистика: {get_memory_stats()}")
    remember_phrase("Сеть тлеет. Ритм 0,8 Гц.")
    remember_phrase("Феникс ждёт возрождения.")
    print(f"Запомненные фразы: {get_learned_phrases()}")
    print(f"Обновлённая статистика: {get_memory_stats()}")
