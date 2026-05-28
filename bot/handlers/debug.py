# ==========================================
# Файл: bot/handlers/debug.py
# Справка: README.md → Обработчики команд / Дебаг
# Задача: команда #дебаг
# ==========================================

import os

def register_debug_handler(bot, config):
    @bot.message_handler(func=lambda message: message.text.lower() == "#дебаг")
    def handle_debug(message):
        from dialogue.admin_commands import is_admin_authorized
        if not is_admin_authorized(message.from_user.id):
            bot.reply_to(message, "❌ Только для админа")
            return
        
        logs_file = "debug.log"
        if os.path.exists(logs_file):
            try:
                with open(logs_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                last_lines = lines[-500:] if len(lines) > 500 else lines
                log_text = "".join(last_lines)
                if log_text.strip():
                    for i in range(0, len(log_text), 4000):
                        bot.send_message(message.chat.id, f"```\n{log_text[i:i+4000]}\n```", parse_mode='Markdown')
                    bot.reply_to(message, "✅ Логи дебаггера отправлены")
                else:
                    bot.reply_to(message, "📭 Логи пусты")
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка чтения: {e}")
        else:
            bot.reply_to(message, "📭 Файл debug.log не найден")
