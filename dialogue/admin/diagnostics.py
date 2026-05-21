# ==========================================
# Файл: dialogue/admin/diagnostics.py
# Справка: README.md → Админка (диагностика)
# Задача: обработчики кнопок "Ошибки", "Лог", "Дебаг"
# Комментарий: показывают содержимое error.log, admin.log, debug.log
# ==========================================

import os

def handle_errors(user_id, bot, chat_id, message_id):
    if os.path.exists("error.log"):
        with open("error.log", "r", encoding="utf-8") as f:
            errors = f.read().strip()
        if errors:
            for i in range(0, len(errors), 4000):
                bot.send_message(user_id, f"```\n{errors[i:i+4000]}\n```", parse_mode='Markdown')
            bot.edit_message_text("✅ Ошибки отправлены в личку", chat_id, message_id)
        else:
            bot.edit_message_text("📭 Ошибок нет", chat_id, message_id)
    else:
        bot.edit_message_text("📭 Файл error.log не найден", chat_id, message_id)

def handle_log(user_id, bot, chat_id, message_id):
    if os.path.exists("admin.log"):
        with open("admin.log", "r", encoding="utf-8") as f:
            log_data = f.read().strip()
        if log_data:
            for i in range(0, len(log_data), 4000):
                bot.send_message(user_id, f"```log\n{log_data[i:i+4000]}\n```", parse_mode='Markdown')
            bot.edit_message_text("✅ Лог отправлен в личку", chat_id, message_id)
        else:
            bot.edit_message_text("📭 Лог пуст", chat_id, message_id)
    else:
        bot.edit_message_text("📭 Файл admin.log не найден", chat_id, message_id)

def handle_debug(user_id, bot, chat_id, message_id):
    debug_file = "debug.log"
    if os.path.exists(debug_file):
        try:
            with open(debug_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            last_lines = lines[-500:] if len(lines) > 500 else lines
            debug_text = "".join(last_lines)
            if debug_text.strip():
                for i in range(0, len(debug_text), 4000):
                    bot.send_message(user_id, f"```\n{debug_text[i:i+4000]}\n```", parse_mode='Markdown')
                bot.edit_message_text("✅ Дебаг отправлен в личку", chat_id, message_id)
            else:
                bot.edit_message_text("📭 Дебаг пуст", chat_id, message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Ошибка чтения дебага: {e}", chat_id, message_id)
    else:
        bot.edit_message_text("📭 Файл debug.log не найден", chat_id, message_id)
