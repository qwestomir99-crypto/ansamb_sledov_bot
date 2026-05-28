# ==========================================
# Файл: services/approval_dialogue.py
# Справка: README.md → Алиса / Диалоговое подтверждение
# Задача: обработка диалогового подтверждения без bot.py
# Комментарий: распознаёт согласие в ответе пользователя
# Зависит от: telebot, services.suggestion_engine, debug_utils
# Вызывается из: bot.py (handle_message) — одной строкой
# ==========================================

import re
import telebot
from services.suggestion_engine import get_last_pending, confirm_last_pending
from debug_utils import debug_log

def log_ad(level, message):
    debug_log("APPROVAL_DIALOGUE", message, level)

def handle_natural_approval(message, bot):
    """
    Обрабатывает обычные сообщения админа.
    Если есть ожидающее предложение — распознаёт согласие или отказ.
    """
    if message.from_user.id != ADMIN_USER_ID:
        return
    
    text = message.text.lower()
    last = get_last_pending()
    if not last:
        return
    
    if re.search(r'(соглас(ен|на)\b|да\b|ок\b|подтвержд(аю|аешь)\b|делай\b)', text):
        if confirm_last_pending(True):
            bot.reply_to(message, f"✅ Изменения применены: {last['description']}")
            bot.reply_to(message, "Можешь проверить. Если что — откатим.")
        else:
            bot.reply_to(message, "❌ Ошибка при применении изменений.")
    elif re.search(r'(нет\b|не надо\b|отклони|отменя)', text):
        confirm_last_pending(False)
        bot.reply_to(message, "❌ Изменения отклонены.")
