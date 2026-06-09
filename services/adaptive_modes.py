# ==========================================
# Файл: services/adaptive_modes.py
# Справка: README.md → Адаптивные режимы
# Задача: динамическое изменение режимов на основе метрик
# Комментарий: добавлена функция get_current_mode_for_routing()
# Зависит от: os, json, time, datetime, collections
# Вызывается из: routing_engine.py
# ==========================================

import os
import json
import time
from datetime import datetime
from collections import deque

# Путь к файлу конфигурации
CONFIG_FILE = os.path.join('dialogue', 'data', 'config.json')
ADAPTIVE_STATE_FILE = "dialogue/data/adaptive_state.json"
ADAPTIVE_CONFIG_FILE = "dialogue/data/adaptive_config.json"

ADAPTIVE_ENABLED = False
ADAPTIVE_COOLDOWN = 3600
DEADEND_TIMEOUT = 7200

metrics_history = deque(maxlen=100)

def load_adaptive_config():
    global ADAPTIVE_ENABLED
    if not os.path.exists(ADAPTIVE_CONFIG_FILE):
        return {"enabled": False}
    try:
        with open(ADAPTIVE_CONFIG_FILE, "r") as f:
            config = json.load(f)
            ADAPTIVE_ENABLED = config.get("enabled", False)
            return config
    except:
        return {"enabled": False}

def save_adaptive_config(config):
    global ADAPTIVE_ENABLED
    os.makedirs(os.path.dirname(ADAPTIVE_CONFIG_FILE), exist_ok=True)
    with open(ADAPTIVE_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    ADAPTIVE_ENABLED = config.get("enabled", False)

def set_adaptive_enabled(enabled):
    config = {"enabled": enabled}
    save_adaptive_config(config)
    print(f"[ADAPTIVE] Адаптивные режимы {'включены' if enabled else 'выключены'}")
    return True

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_adaptive_state():
    if not os.path.exists(ADAPTIVE_STATE_FILE):
        return {
            "last_switch": 0,
            "current_adaptive_mode": None,
            "deadend_count": 0,
            "last_return_to_etalon": 0
        }
    try:
        with open(ADAPTIVE_STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "last_switch": 0,
            "current_adaptive_mode": None,
            "deadend_count": 0,
            "last_return_to_etalon": 0
        }

def save_adaptive_state(state):
    try:
        os.makedirs(os.path.dirname(ADAPTIVE_STATE_FILE), exist_ok=True)
        with open(ADAPTIVE_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except:
        pass

def collect_metrics():
    metrics = {
        "errors_last_hour": count_errors_last_hour(),
        "commands_last_hour": count_commands_last_hour(),
        "is_weekend": datetime.now().weekday() >= 5,
        "hour": datetime.now().hour,
        "last_publication_age": get_last_publication_age()
    }
    metrics_history.append({**metrics, "timestamp": time.time()})
    return metrics

def count_errors_last_hour():
    if not os.path.exists("error.log"):
        return 0
    try:
        with open("error.log", "r") as f:
            return len(f.readlines())
    except:
        return 0

def count_commands_last_hour():
    if not os.path.exists("admin.log"):
        return 0
    try:
        with open("admin.log", "r") as f:
            lines = f.readlines()
        return sum(1 for line in lines if "#говори" in line or "#меню" in line)
    except:
        return 0

def get_last_publication_age():
    pubs_file = "publications.json"
    if not os.path.exists(pubs_file):
        return 999
    try:
        with open(pubs_file, "r") as f:
            pubs = json.load(f)
        if not pubs:
            return 999
        last_pub = max(pubs, key=lambda x: x.get("publish_at", 0))
        return int((time.time() - last_pub.get("publish_at", 0)) / 60)
    except:
        return 999

def get_adaptive_mode(metrics):
    errors = metrics.get("errors_last_hour", 0)
    commands = metrics.get("commands_last_hour", 0)
    is_weekend = metrics.get("is_weekend", False)
    hour = metrics.get("hour", 0)
    last_pub_age = metrics.get("last_publication_age", 999)

    if errors > 10:
        return "авральный"
    if hour < 6 or hour > 23:
        if commands < 3 and last_pub_age > 120:
            return "ночной"
    if commands > 20 or (is_weekend and commands > 10):
        return "ускоренный"
    if commands < 3 and last_pub_age > 60:
        return "замедленный"
    if commands == 0 and last_pub_age > 180:
        return "сон"
    return "обычный"

def is_dead_end(adaptive_mode, metrics):
    errors = metrics.get("errors_last_hour", 0)
    commands = metrics.get("commands_last_hour", 0)
    last_pub_age = metrics.get("last_publication_age", 999)

    if errors > 15:
        return True
    if commands == 0 and last_pub_age > 180:
        return True
    return False

def get_etalon_mode_by_time():
    config = load_config()
    current_hour = datetime.now().hour
    modes = config.get("modes", {})
    for mode_name, mode_config in modes.items():
        start = mode_config.get("hour_start")
        end = mode_config.get("hour_end")
        if start <= end:
            if start <= current_hour < end:
                return mode_name
        else:
            if current_hour >= start or current_hour < end:
                return mode_name
    return "день"

def get_adaptive_interval(base_interval, adaptive_mode):
    if adaptive_mode == "ускоренный":
        return max(15, base_interval // 2)
    elif adaptive_mode == "замедленный":
        return min(480, base_interval * 2)
    elif adaptive_mode in ["авральный", "сон"]:
        return 0
    return base_interval

def get_current_adaptive_mode():
    load_adaptive_config()
    if not ADAPTIVE_ENABLED:
        return get_etalon_mode_by_time()
    
    state = load_adaptive_state()
    metrics = collect_metrics()
    adaptive_mode = get_adaptive_mode(metrics)
    
    prev_mode = state.get("current_adaptive_mode")
    if prev_mode and prev_mode != "обычный" and is_dead_end(adaptive_mode, metrics):
        state["last_return_to_etalon"] = time.time()
        state["deadend_count"] += 1
        state["current_adaptive_mode"] = None
        save_adaptive_state(state)
        return get_etalon_mode_by_time()
    
    now = time.time()
    if adaptive_mode != state.get("current_adaptive_mode"):
        if now - state.get("last_switch", 0) > ADAPTIVE_COOLDOWN:
            state["last_switch"] = now
            state["current_adaptive_mode"] = adaptive_mode
            save_adaptive_state(state)
        else:
            adaptive_mode = state.get("current_adaptive_mode", "обычный")
    else:
        if adaptive_mode not in [None, "обычный"]:
            state["current_adaptive_mode"] = adaptive_mode
            save_adaptive_state(state)
    
    return adaptive_mode

def get_current_mode_for_routing():
    """Возвращает текущий режим для маршрутизации"""
    return get_current_adaptive_mode()

def get_adaptive_quotes_interval(base_interval):
    return get_adaptive_interval(base_interval, get_current_adaptive_mode())

def get_adaptive_publisher_interval(base_interval):
    return get_adaptive_interval(base_interval, get_current_adaptive_mode())

def should_adaptive_publish():
    return get_current_adaptive_mode() not in ["авральный", "сон"]

def reset_to_etalon():
    state = load_adaptive_state()
    state["current_adaptive_mode"] = None
    state["deadend_count"] = 0
    state["last_return_to_etalon"] = time.time()
    save_adaptive_state(state)
    print("[ADAPTIVE] Принудительный сброс к эталонным режимам")
    return True
