# ==========================================
# Файл: new_debugger/debug_utils.py
# Задача: централизованный дебаггер с отправкой в Telegram
# Комментарий: управляется через админку, логи приходят в личку админу
# ==========================================

import os
import json
import requests
from datetime import datetime

CONFIG_FILE = "debug_config.json"
ADMIN_ID = int(os.environ.get("ADMIN_USER_ID", 0))
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Буфер для накопления логов (при интервале > 0)
log_buffer = []
last_sent = 0

def load_config():
    """Загружает настройки дебаггера из JSON-файла"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # Настройки по умолчанию
    return {
        "enabled": False,           # Дебаггер выключен
        "modules": [],              # Какие модули логировать (пусто = все)
        "interval_minutes": 0,      # 0 = сразу, >0 = накопление
        "send_to_telegram": True,   # Отправлять в Telegram
        "last_sent": 0
    }

def save_config(config):
    """Сохраняет настройки дебаггера"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except:
        pass

def send_to_telegram(text):
    """Отправляет сообщение админу в Telegram"""
    if not BOT_TOKEN or not ADMIN_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": ADMIN_ID, "text": text, "parse_mode": "Markdown"},
            timeout=2
        )
    except:
        pass

def flush_logs():
    """Отправляет накопленные логи одной пачкой"""
    global log_buffer, last_sent
    if not log_buffer:
        return
    
    # Берём последние 20 строк, чтобы не превысить лимит Telegram
    text = "\n".join(log_buffer[-20:])
    send_to_telegram(f"📦 *Накопленные логи:*\n```\n{text}\n```")
    log_buffer.clear()
    
    config = load_config()
    config["last_sent"] = datetime.now().timestamp()
    save_config(config)

def debug_log(module, message, level="INFO"):
    """
    Основная функция логирования.
    - Если дебаггер выключен — ничего не делает.
    - Если модуль не в списке — пропускает.
    - Отправляет в Telegram (сразу или с накоплением).
    """
    config = load_config()
    if not config.get("enabled", False):
        return
    
    # Проверка модуля
    modules = config.get("modules", [])
    if modules and module not in modules:
        return
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] [{module}] {level}: {message}"
    
    # Если нужно отправлять в Telegram
    if config.get("send_to_telegram", True):
        interval = config.get("interval_minutes", 0)
        if interval <= 0:
            # Отправляем сразу
            send_to_telegram(log_entry)
        else:
            # Накопление
            log_buffer.append(log_entry)
            now = datetime.now().timestamp()
            last = config.get("last_sent", 0)
            if now - last >= interval * 60:
                flush_logs()
    
    # Для обратной совместимости — пишем в консоль
    print(log_entry)

def log_error(module, error):
    """Ошибки всегда логируются (с уровнем ERROR)"""
    debug_log(module, str(error), level="ERROR")
