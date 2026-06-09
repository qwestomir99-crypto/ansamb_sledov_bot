# ==========================================
# Файл: Alice/disabled.py
# Справка: README.md → Алиса / Переключатель
# Задача: выключает Алису (по умолчанию — выключена)
# Комментарий: просто меняет флаг в config.json
# Зависит от: os, json
# Вызывается из: config.json (автоматически)
# ==========================================

import os
import json

# Путь к файлу конфигурации
CONFIG_FILE = os.path.join('dialogue', 'data', 'config.json')

def is_alice_disabled():
    """Возвращает True, если Алиса выключена (по умолчанию)"""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return not config.get("alice", {}).get("enabled", False)
    except:
        return True

def disable_alice():
    """Выключает Алису (записывает в config.json)"""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        if "alice" not in config:
            config["alice"] = {}
        config["alice"]["enabled"] = False
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print("[ALICE] Алиса выключена.")
        return True
    except Exception as e:
        print(f"[ALICE] Ошибка выключения: {e}")
        return False

def enable_alice():
    """Включает Алису (записывает в config.json)"""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        if "alice" not in config:
            config["alice"] = {}
        config["alice"]["enabled"] = True
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print("[ALICE] Алиса включена.")
        return True
    except Exception as e:
        print(f"[ALICE] Ошибка включения: {e}")
        return False

if __name__ == "__main__":
    # Тест: выключаем Алису (по умолчанию)
    disable_alice()
    print(f"Алиса выключена: {is_alice_disabled()}")
