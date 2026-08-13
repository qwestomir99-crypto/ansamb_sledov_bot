# ==========================================
# Файл: render_callbacks.py (для Render)
# Справка: README.md → Telegram прокси / Render / Кнопки
# Задача: все обработчики callback'ов на Render
# Комментарий: вызывается из bot.py на Render
# Зависит от: telebot
# Вызывается из: bot.py (Render)
# Версия: 1.0 — единый список всех кнопок
# ==========================================

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def build_keyboard(buttons_data):
    """Строит клавиатуру из JSON-списка"""
    keyboard = InlineKeyboardMarkup()
    for row in buttons_data:
        buttons_row = []
        for btn in row:
            buttons_row.append(InlineKeyboardButton(
                text=btn.get("text", "?"),
                callback_data=btn.get("callback_data", "none")
            ))
        keyboard.row(*buttons_row)
    return keyboard

def register_callbacks(bot):
    """Регистрирует все callback-обработчики"""
    
    @bot.callback_query_handler(func=lambda call: True)
    def handle_all(call):
        data = call.data
        cid = call.message.chat.id
        mid = call.message.message_id
        
        # ... обработка всех callback'ов
