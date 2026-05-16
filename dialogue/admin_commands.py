
import os
import json
import time
from datetime import datetime
from dialogue.ping_modes import apply_ping_mode

CONFIG_FILE = "config.json"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))

def log_admin_action(user_id, action, result):
    with open("admin.log", "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} | user:{user_id} | {action} | {result}\n")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def handle_admin_command(message, bot):
    user_id = message.from_user.id
    if user_id != ADMIN_USER_ID:
        bot.reply_to(message, "❌ Доступ запрещён. Вы не администратор.")
        log_admin_action(user_id, "unauthorized_access", "blocked")
        return

    text = message.text.split()
    if len(text) < 2:
        bot.reply_to(message, "❌ Неверный формат. Используй: #админ <пароль> <команда>")
        return

    password = text[1]
    if password != ADMIN_PASSWORD:
        bot.reply_to(message, "❌ Неверный пароль")
        log_admin_action(user_id, "wrong_password", "blocked")
        return

    if len(text) < 3:
        bot.reply_to(message, "❌ Укажи команду: ping <секунды> | mode <утро/день/вечер/сон>")
        return

    command = text[2]
    config = load_config()

    if command == "ping" and len(text) >= 4:
        try:
            new_interval = int(text[3])
            config["ping_interval"] = new_interval
            save_config(config)
            apply_ping_mode()
            bot.reply_to(message, f"✅ Пинг установлен на {new_interval} секунд")
            log_admin_action(user_id, f"ping {new_interval}", "success")
        except ValueError:
            bot.reply_to(message, "❌ Интервал должен быть числом")

    elif command == "mode" and len(text) >= 4:
        new_mode = text[3]
        if new_mode in ["утро", "день", "вечер", "сон"]:
            config["activity_mode"] = new_mode
            save_config(config)
            bot.reply_to(message, f"✅ Режим активности установлен на {new_mode}")
            log_admin_action(user_id, f"mode {new_mode}", "success")
        else:
            bot.reply_to(message, "❌ Режим должен быть: утро, день, вечер, сон")

    else:
        bot.reply_to(message, "❌ Неизвестная команда")
        log_admin_action(user_id, f"unknown command: {command}", "failed")
