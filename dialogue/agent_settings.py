# ==========================================
# Файл: dialogue/agent_settings.py
# Справка: README.md → Агент / Настройки
# Задача: загрузка и сохранение настроек агента
# Комментарий: хранится в library/agent_settings.json
# ==========================================

import os
import json

SETTINGS_FILE = "library/agent_settings.json"

def get_agent_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"temperature": 0.7, "max_tokens": 500}
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"temperature": 0.7, "max_tokens": 500}

def save_agent_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

def set_agent_temperature(temp):
    s = get_agent_settings()
    s["temperature"] = max(0.1, min(1.5, float(temp)))
    save_agent_settings(s)

def set_agent_max_tokens(tokens):
    s = get_agent_settings()
    s["max_tokens"] = int(tokens)
    save_agent_settings(s)
