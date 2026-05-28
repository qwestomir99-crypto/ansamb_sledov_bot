# ==========================================
# Файл: dialogue/approve_commands.py
# Справка: README.md → Алиса / Утверждение предложений
# Задача: обработчик команды #подтверди для админа
# Комментарий: вынесен из bot.py для чистоты
# Зависит от: telebot, services.suggestion_engine, debug_utils
# Вызывается из: bot.py (импорт)
# ==========================================

import telebot
from services.suggestion_engine import approve_suggestion, list_pending_suggestions
from debug_utils import debug_log

def log_ac(level, message):
    debug_log("APPROVE_COMMANDS", message, level)

def register_approve_handlers(bot, ADMIN_USER_ID):
    @bot.message_handler(commands=['approve'])
    def approve_suggestion_cmd(message):
        if message.from_user.id != ADMIN_USER_ID:
            bot.reply_to(message, "❌ Только для админа")
            return
        try:
            suggestion_id = int(message.text.split()[1])
            if approve_suggestion(suggestion_id):
                bot.reply_to(message, f"✅ Предложение {suggestion_id} утверждено")
            else:
                bot.reply_to(message, f"❌ Предложение {suggestion_id} не найдено")
        except:
            bot.reply_to(message, "❌ Использование: /approve <ID>")
    
    @bot.message_handler(commands=['pending'])
    def list_pending_cmd(message):
        if message.from_user.id != ADMIN_USER_ID:
            bot.reply_to(message, "❌ Только для админа")
            return
        pending = list_pending_suggestions()
        if not pending:
            bot.reply_to(message, "📭 Нет ожидающих предложений")
            return
        text = "📋 *Ожидающие предложения:*\n\n"
        for s in pending:
            text += f"• #{s['id']} — {s['description']}\n"
        bot.reply_to(message, text, parse_mode='Markdown')
