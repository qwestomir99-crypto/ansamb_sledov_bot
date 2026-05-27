# ==========================================
# Модуль: dialogue/agent_memory_supabase.py
# Справка: README.md → Память агента
# Задача: хранение важных фраз и диалогов (долговременная память)
# Комментарий: использует Supabase с фоллбэком на memory.json
# Зависит от: json, os, datetime, services.supabase_client, debug_utils
# Вызывается из: agent.py (опционально), evolve_agent.py
# ==========================================

import os
import json
from datetime import datetime
from debug_utils import debug_log
from services.supabase_client import db_insert, db_select

# ==========================================
# КОНСТАНТЫ
# ==========================================
MEMORY_TABLE = "memory"
MEMORY_FALLBACK_FILE = "agent_data/memory.json"

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def _ensure_dir():
    os.makedirs(os.path.dirname(MEMORY_FALLBACK_FILE), exist_ok=True)

# ==========================================
# ЗАГРУЗКА ПАМЯТИ
# ==========================================
def get_memory():
    """
    Загружает память агента.
    Сначала пытается взять из Supabase, при ошибке — из memory.json.
    """
    # Попытка из базы
    result = db_select(MEMORY_TABLE, limit=100, fallback_file=None)
    if result:
        # Преобразуем в структуру, ожидаемую агентов
        return {
            "learned_phrases": [row.get("phrase") for row in result if row.get("type") == "phrase"],
            "important_dialogues": [
                {
                    "timestamp": row.get("created_at"),
                    "question": row.get("question"),
                    "answer": row.get("answer"),
                    "user_id": row.get("user_id")
                }
                for row in result if row.get("type") == "dialogue"
            ],
            "last_cleanup": datetime.now().isoformat()
        }
    
    # Фоллбэк на файл
    _ensure_dir()
    if os.path.exists(MEMORY_FALLBACK_FILE):
        with open(MEMORY_FALLBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "learned_phrases": [],
        "important_dialogues": [],
        "last_cleanup": datetime.now().isoformat()
    }

# ==========================================
# СОХРАНЕНИЕ ПАМЯТИ
# ==========================================
def save_memory(memory):
    """
    Сохраняет память агента.
    Сначала пытается записать в Supabase, при ошибке — в memory.json.
    """
    # Попытка в базу
    for phrase in memory.get("learned_phrases", []):
        db_insert(MEMORY_TABLE, {"phrase": phrase, "type": "phrase"}, fallback_file=MEMORY_FALLBACK_FILE)
    
    for dialogue in memory.get("important_dialogues", []):
        db_insert(
            MEMORY_TABLE,
            {
                "question": dialogue.get("question"),
                "answer": dialogue.get("answer"),
                "user_id": dialogue.get("user_id"),
                "type": "dialogue"
            },
            fallback_file=MEMORY_FALLBACK_FILE
        )
    
    # Фоллбэк на файл (если база не ответила)
    _ensure_dir()
    with open(MEMORY_FALLBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

# ==========================================
# ОСТАЛЬНЫЕ ФУНКЦИИ (без изменений)
# ==========================================
def remember_phrase(phrase):
    memory = get_memory()
    if phrase not in memory["learned_phrases"]:
        memory["learned_phrases"].append(phrase)
        if len(memory["learned_phrases"]) > 100:
            memory["learned_phrases"] = memory["learned_phrases"][-100:]
        save_memory(memory)
        debug_log("AGENT_MEMORY", f"Запомнена фраза: {phrase[:50]}...", "INFO")
        return True
    return False

def forget_phrase(phrase):
    memory = get_memory()
    if phrase in memory["learned_phrases"]:
        memory["learned_phrases"].remove(phrase)
        save_memory(memory)
        debug_log("AGENT_MEMORY", f"Фраза забыта: {phrase[:50]}...", "INFO")
        return True
    return False

def get_learned_phrases(limit=10):
    memory = get_memory()
    return memory.get("learned_phrases", [])[-limit:]

def remember_dialogue(question, answer, user_id=None):
    memory = get_memory()
    dialogue = {
        "timestamp": datetime.now().isoformat(),
        "question": question[:200],
        "answer": answer[:200],
        "user_id": user_id
    }
    memory["important_dialogues"].append(dialogue)
    if len(memory["important_dialogues"]) > 50:
        memory["important_dialogues"] = memory["important_dialogues"][-50:]
    save_memory(memory)
    debug_log("AGENT_MEMORY", f"Диалог запомнен: {question[:50]}...", "INFO")
    return True

def get_important_dialogues(limit=5):
    memory = get_memory()
    return memory.get("important_dialogues", [])[-limit:]

def get_memory_stats():
    memory = get_memory()
    return {
        "phrases_count": len(memory.get("learned_phrases", [])),
        "dialogues_count": len(memory.get("important_dialogues", [])),
        "last_cleanup": memory.get("last_cleanup", "никогда")
    }
