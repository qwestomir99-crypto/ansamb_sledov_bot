# ==========================================
# Файл: alice/core.py
# Справка: README.md → Алиса / Генератор контента
# Задача: генерация уникальных подписей для постов (фото, видео, ссылки)
# Комментарий: использует ask_agent() для вызова Yandex GPT.
#              На старте выключен, включится после 1 июня.
#              Работает в паре с prompts.py.
# Зависит от: dialogue.agent, debug_utils, config.json
# Вызывается из: quotes.py, autoposter.py (после включения)
# ==========================================

import os
import json
from datetime import datetime
from debug_utils import debug_log
from dialogue.agent import ask_agent

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
CONFIG_FILE = "config.json"
ALICE_ENABLED = False  # По умолчанию выключена

def log_alice(level, message):
    debug_log("ALICE", message, level)

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def is_alice_enabled():
    """Возвращает True, если Алиса включена в config.json"""
    config = load_config()
    return config.get("alice", {}).get("enabled", False)

# ==========================================
# ГЕНЕРАЦИЯ КОНТЕНТА
# ==========================================
def generate_caption(media_type, title="", author="", tags=None):
    """
    Генерирует короткую подпись (1-2 предложения) для поста.
    
    Args:
        media_type: "photo", "video", "link"
        title: название медиа
        author: автор/канал
        tags: список хештегов (опционально)
    
    Returns:
        str: подпись для поста
    """
    if not is_alice_enabled():
        log_alice("WARNING", "Алиса выключена, возвращаю заглушку")
        return "Сеть тлеет. Ритм 0,8 Гц."
    
    # Формируем промпт в зависимости от типа
    from alice.prompts import get_prompt
    prompt = get_prompt(media_type, title, author, tags)
    
    if not prompt:
        log_alice("ERROR", "Не удалось получить промпт")
        return "Сеть тлеет. Ритм 0,8 Гц."
    
    # Вызываем агента
    try:
        response = ask_agent(prompt, user_id="alice")
        # Обрезаем до разумной длины
        if len(response) > 300:
            response = response[:300] + "..."
        log_alice("INFO", f"Сгенерирована подпись для {media_type}: {response[:50]}...")
        return response
    except Exception as e:
        log_alice("ERROR", f"Ошибка генерации: {e}")
        return "Сеть тлеет. Ритм 0,8 Гц."

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def enable_alice():
    """Включает Алису в config.json"""
    config = load_config()
    if "alice" not in config:
        config["alice"] = {}
    config["alice"]["enabled"] = True
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    log_alice("INFO", "Алиса включена")

def disable_alice():
    """Выключает Алису в config.json"""
    config = load_config()
    if "alice" not in config:
        config["alice"] = {}
    config["alice"]["enabled"] = False
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    log_alice("INFO", "Алиса выключена")

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ АЛИСЫ ===")
    print(f"Алиса включена: {is_alice_enabled()}")
    print(f"Подпись для видео: {generate_caption('video', 'Тестовое видео', 'Ансамбль')}")
