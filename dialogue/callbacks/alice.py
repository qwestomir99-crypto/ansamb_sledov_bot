# ==========================================
# Файл: dialogue/callbacks/alice.py
# Справка: README.md → Обработчики кнопок / Алиса
# Задача: обработка callback'ов для управления Алисой
# Комментарий: вынесен из callbacks.py
# Зависит от: telebot, Alice.alice_admin, debug_utils
# Вызывается из: callbacks/__init__.py
# ==========================================

import telebot
from Alice.alice_admin import toggle_alice
from debug_utils import debug_log

def register_alice_callbacks(bot: telebot.TeleBot, config: dict):
    """Регистрирует callback'и для Алисы"""
    
    @bot.callback_query_handler(func=lambda call: call.data == "toggle_alice")
    def callback_toggle_alice(call):
        debug_log("CALLBACK", f"Переключение Алисы от {call.from_user.id}")
        toggle_alice(call, bot)
        bot.answer_callback_query(call.id)
