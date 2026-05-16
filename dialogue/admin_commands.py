import os
import json
import time
from datetime import datetime, timedelta
from dialogue.ping_modes import apply_ping_mode

CONFIG_FILE = "config.json"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))

MODES = ["утро", "день", "вечер", "сон"]

GREETINGS = {
    "утро": "🌅 Доброе утро, сапёр. Сеть тлеет, ритм 0,8 Гц стабилен.",
    "день": "☀️ Хорошего дня. Не забывай #Тлеем.",
    "вечер": "🌙 Спокойного вечера. Наблюдение продолжается.",
    "сон": "😴 Режим сна. Старший брат отдыхает. Вопросы — утром."
}

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
        bot.reply_to(message, f"❌ Используй: #админ <пароль> <команда>\nДоступные режимы: {', '.join(MODES)}")
        return

    password = text[1]
    if password != ADMIN_PASSWORD:
        bot.reply_to(message, "❌ Неверный пароль")
        log_admin_action(user_id, "wrong_password", "blocked")
        return

    if len(text) == 2:
        bot.reply_to(message, f"📋 Доступные режимы: {', '.join(MODES)}. Используй: #админ <пароль> mode <режим> [время]")
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

    elif command == "mode":
        if len(text) < 4:
            bot.reply_to(message, f"❌ Укажи режим: {', '.join(MODES)}. Пример: #админ {ADMIN_PASSWORD} mode утро 14:30")
            return
        
        new_mode = text[3]
        if new_mode not in MODES:
            bot.reply_to(message, f"❌ Режим должен быть: {', '.join(MODES)}")
            return
        
        start_time_str = text[4] if len(text) > 4 else None
        
        if start_time_str:
            try:
                start_hour, start_minute = map(int, start_time_str.split(':'))
                start_time = datetime.now().replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                if start_time < datetime.now():
                    start_time = start_time + timedelta(days=1)
                config["force_mode"] = new_mode
                config["force_mode_until"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
                save_config(config)
                bot.reply_to(message, f"✅ Режим «{new_mode}» установлен с {start_time.strftime('%H:%M')}\n\n{GREETINGS.get(new_mode, '')}")
                log_admin_action(user_id, f"mode {new_mode} at {start_time_str}", "success")
            except:
                bot.reply_to(message, "❌ Неверный формат времени. Используй ЧЧ:ММ")
        else:
            config["force_mode"] = new_mode
            config["force_mode_until"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_config(config)
            bot.reply_to(message, f"✅ Режим «{new_mode}» установлен сейчас\n\n{GREETINGS.get(new_mode, '')}")
            log_admin_action(user_id, f"mode {new_mode} now", "success")

    elif command == "ошибки":
        if os.path.exists("error.log"):
            with open("error.log", "r", encoding="utf-8") as f:
                errors = f.read().strip()
            if errors:
                # Отправляем частями, если много
                for i in range(0, len(errors), 4000):
                    bot.send_message(user_id, errors[i:i+4000])
                bot.reply_to(message, "✅ Отчёт об ошибках отправлен в личку")
            else:
                bot.reply_to(message, "📭 Ошибок нет")
        else:
            bot.reply_to(message, "📭 Файл error.log не найден")
        log_admin_action(user_id, "requested_errors", "success")

    else:
        bot.reply_to(message, "❌ Неизвестная команда")
        log_admin_action(user_id, f"unknown command: {command}", "failed")
