# ==========================================
# Файл: services/agent_config.py
# Справка: README.md → Агент / Конфигурация
# Задача: чтение и применение правил из agent_rules.txt
# Комментарий: вызывается при старте и при изменении правил
# Зависит от: os, debug_utils
# Вызывается из: bot.py (при старте), suggestion_engine.py (при подтверждении)
# ==========================================

import os
import re
from debug_utils import debug_log

RULES_FILE = "Alice/agent_rules.txt"

def log_ac(level, message):
    debug_log("AGENT_CONFIG", message, level)

def load_rules():
    if not os.path.exists(RULES_FILE):
        log_ac("WARNING", f"{RULES_FILE} не найден")
        return {}
    
    rules = {}
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                rules[key.strip()] = value.strip()
    log_ac("INFO", f"Загружено {len(rules)} правил")
    return rules

def apply_rules():
    rules = load_rules()
    # Применяем правила к агенту
    return rules
