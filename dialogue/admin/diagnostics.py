# ==========================================
# Файл: dialogue/admin/diagnostics.py
# Справка: README.md → Админка (диагностика)
# Задача: меню диагностики и обработчики кнопок
# ==========================================

import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_diagnostics_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📋 admin.log", callback_data="view_admin_log"),
        InlineKeyboardButton("❌ error.log", callback_data="view_error_log"),
    )
    keyboard.add(
        InlineKeyboardButton("🐛 debug.log", callback_data="view_debug_log"),
        InlineKeyboardButton("🧹 Очистить логи", callback_data="clear_logs"),
    )
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="back_to_admin"))
    return keyboard

def register_diagnostics_callbacks(bot, config):
    @bot.callback_query_handler(func=lambda call: call.data == "view_admin_log")
    def view_admin_log(call):
        if os.path.exists("admin.log"):
            with open("admin.log", "r", encoding="utf-8") as f:
                log_data = f.read().strip()[-4000:]
            if log_data:
                bot.send_message(call.from_user.id, f"```\n{log_data}\n```", parse_mode='Markdown')
                bot.answer_callback_query(call.id, "✅ Отправлено в личку")
            else:
                bot.answer_callback_query(call.id, "📭 Лог пуст")
        else:
            bot.answer_callback_query(call.id, "📭 Файл не найден")
    
    @bot.callback_query_handler(func=lambda call: call.data == "view_error_log")
    def view_error_log(call):
        if os.path.exists("error.log"):
            with open("error.log", "r", encoding="utf-8") as f:
                log_data = f.read().strip()[-4000:]
            if log_data:
                bot.send_message(call.from_user.id, f"```\n{log_data}\n```", parse_mode='Markdown')
                bot.answer_callback_query(call.id, "✅ Отправлено в личку")
            else:
                bot.answer_callback_query(call.id, "📭 Лог пуст")
        else:
            bot.answer_callback_query(call.id, "📭 Файл не найден")
    
    @bot.callback_query_handler(func=lambda call: call.data == "view_debug_log")
    def view_debug_log(call):
        if os.path.exists("debug.log"):
            with open("debug.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
                last_lines = lines[-500:] if len(lines) > 500 else lines
                log_data = "".join(last_lines)[-4000:]
            if log_data.strip():
                bot.send_message(call.from_user.id, f"```\n{log_data}\n```", parse_mode='Markdown')
                bot.answer_callback_query(call.id, "✅ Отправлено в личку")
            else:
                bot.answer_callback_query(call.id, "📭 Дебаг пуст")
        else:
            bot.answer_callback_query(call.id, "📭 Файл не найден")
    
    @bot.callback_query_handler(func=lambda call: call.data == "clear_logs")
    def clear_logs(call):
        for f in ["admin.log", "error.log", "debug.log"]:
            if os.path.exists(f):
                open(f, "w").close()
        bot.answer_callback_query(call.id, "🧹 Логи очищены")
