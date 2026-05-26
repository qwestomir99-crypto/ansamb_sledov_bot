# ==========================================
# Файл: alice/core.py
# Справка: README.md → Алиса / Генератор контента
# Задача: генерация уникальных подписей для постов (фото, видео, ссылки)
# Комментарий: промпты лежат в alice/prompts/, core.py только выбирает и вызывает.
#              На старте выключен, включится после 1 июня.
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
ALICE_ENABLED = False

def log_alice(level, message):
    debug_log("ALICE", message, level)

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def is_alice_enabled():
    config = load_config()
    return config.get("alice", {}).get("enabled", False)

# ==========================================
# ЗАГРУЗКА ПРОМПТОВ ИЗ ПАПКИ prompts/
# ==========================================
def load_prompt(media_type, title="", author="", tags=None):
    """
    Загружает промпт из alice/prompts/{media_type}.py и подставляет параметры.
    """
    try:
        module = __import__(f"alice.prompts.{media_type}", fromlist=["get_prompt"])
        return module.get_prompt(title, author, tags)
    except ImportError:
        log_alice("ERROR", f"Промпт для {media_type} не найден")
        return None
    except Exception as e:
        log_alice("ERROR", f"Ошибка загрузки промпта: {e}")
        return None

def load_library_context():
    """Загружает контекст библиотеки из alice/prompts/library.py"""
    try:
        module = __import__("alice.prompts.library", fromlist=["get_context"])
        return module.get_context()
    except:
        return ""

def load_role_context(role=None):
    """Загружает контекст роли из alice/prompts/roles.py"""
    try:
        module = __import__("alice.prompts.roles", fromlist=["get_role_context"])
        return module.get_role_context(role)
    except:
        return ""

# ==========================================
# ГЕНЕРАЦИЯ КОНТЕНТА
# ==========================================
def generate_caption(media_type, title="", author="", tags=None, role=None):
    if not is_alice_enabled():
        log_alice("WARNING", "Алиса выключена, возвращаю заглушку")
        return "Сеть тлеет. Ритм 0,8 Гц."
    
    # Загружаем промпт
    prompt = load_prompt(media_type, title, author, tags)
    if not prompt:
        return "Сеть тлеет. Ритм 0,8 Гц."
    
    # Добавляем контекст библиотеки
    library = load_library_context()
    role_ctx = load_role_context(role)
    
    full_prompt = f"{library}\n\n{role_ctx}\n\n{prompt}"
    
    try:
        response = ask_agent(full_prompt, user_id="alice")
        if len(response) > 300:
            response = response[:300] + "..."
        log_alice("INFO", f"Сгенерирована подпись для {media_type}: {response[:50]}...")
        return response
    except Exception as e:
        log_alice("ERROR", f"Ошибка генерации: {e}")
        return "Сеть тлеет. Ритм 0,8 Гц."

# ==========================================
# ВКЛЮЧЕНИЕ/ВЫКЛЮЧЕНИЕ
# ==========================================
def enable_alice():
    config = load_config()
    if "alice" not in config:
        config["alice"] = {}
    config["alice"]["enabled"] = True
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    log_alice("INFO", "Алиса включена")

def disable_alice():
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
