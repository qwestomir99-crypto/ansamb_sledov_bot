import json
import telebot
from ping_modes import apply_ping_mode

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def handle_admin_command(message, bot):
    text = message.text.split()
    if len(text) < 2:
        bot.reply_to(message, "❌ Неверный формат. Используй: #админ <пароль> <команда>")
        return
    password = text[1]
    config = load_config()
    if password != config.get("admin_password"):
        bot.reply_to(message, "❌ Неверный пароль")
        return
    if len(text) < 3:
        bot.reply_to(message, "❌ Укажи команду: ping <секунды> | mode <утро/день/вечер/сон>")
        return
    command = text[2]
    if command == "ping" and len(text) >= 4:
        try:
            new_interval = int(text[3])
            config["ping_interval"] = new_interval
            save_config(config)
            apply_ping_mode()
            bot.reply_to(message, f"✅ Пинг установлен на {new_interval} секунд")
        except ValueError:
            bot.reply_to(message, "❌ Интервал должен быть числом")
    elif command == "mode" and len(text) >= 4:
        new_mode = text[3]
        if new_mode in ["утро", "день", "вечер", "сон"]:
            config["activity_mode"] = new_mode
            save_config(config)
            bot.reply_to(message, f"✅ Режим активности установлен на {new_mode}")
        else:
            bot.reply_to(message, "❌ Режим должен быть: утро, день, вечер, сон")
    else:
        bot.reply_to(message, "❌ Неизвестная команда")
