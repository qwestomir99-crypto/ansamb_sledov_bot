# ==========================================
# Файл: dialogue/callbacks/user.py
# Справка: README.md → Обработчики кнопок / Гостевые
# Задача: обработка callback'ов для гостевых кнопок
# Комментарий: обработчик НАСТРОЕНИЯ ВРЕМЕННО ОТКЛЮЧЁН (циклический импорт)
# Зависит от: telebot, dialogue.admin_commands, debug_utils
# Вызывается из: callbacks/__init__.py
# ==========================================

import telebot
from dialogue.admin_commands import show_dialog_ui, handle_admin_command
from debug_utils import debug_log

def register_user_callbacks(bot: telebot.TeleBot, config: dict):
    """Регистрирует callback'и для гостевых кнопок"""
    
    @bot.callback_query_handler(func=lambda call: call.data == "user_help")
    def callback_user_help(call):
        debug_log("CALLBACK", f"Помощь пользователю {call.from_user.id}")
        bot.edit_message_text(
            "📖 *Справка*\n\n"
            "Доступные команды:\n"
            "• `#меню` — открыть меню\n"
            "• `#админ` — войти в админ-панель\n"
            "• `#тлеем` — цитата\n"
            "• `#фиксируем` — подтверждение ритма\n"
            "• `#вспышка` — импульс\n"
            "• `#дышим` — пинг бота\n\n"
            "Также доступны кнопки в меню.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "user_tleem")
    def callback_user_tleem(call):
        debug_log("CALLBACK", f"#тлеем от {call.from_user.id}")
        from dialogue.quotes import get_quotes_list
        import random
        quotes = get_quotes_list()
        if quotes:
            quote = random.choice(quotes)
            bot.edit_message_text(
                f"👁️ {quote}",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        else:
            bot.edit_message_text(
                "📭 База цитат пуста.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "user_fix")
    def callback_user_fix(call):
        debug_log("CALLBACK", f"#фиксируем от {call.from_user.id}")
        bot.edit_message_text(
            "🔒 Фиксация принята. Ритм 0,8 Гц подтверждён.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "user_flash")
    def callback_user_flash(call):
        debug_log("CALLBACK", f"#вспышка от {call.from_user.id}")
        bot.edit_message_text(
            "⚡ Импульс зафиксирован. Синхронизация завершена. QSL.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    # ==========================================
    # ОБРАБОТЧИК НАСТРОЕНИЯ ВРЕМЕННО ОТКЛЮЧЁН
    # ==========================================
    # @bot.callback_query_handler(func=lambda call: call.data == "mood_menu")
    # def callback_mood_menu(call):
    #     debug_log("CALLBACK", f"Меню настроения от {call.from_user.id}")
    #     from dialogue.callbacks.mood import show_mood_menu_handler as show_mood_menu
    #     show_mood_menu(call, bot)
    #     bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "start_dialog")
    def callback_start_dialog(call):
        debug_log("CALLBACK", f"Начало диалога от {call.from_user.id}")
        show_dialog_ui(call, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "admin_login")
    def callback_admin_login(call):
        debug_log("CALLBACK", f"Запрос входа в админку от {call.from_user.id}")
        class FakeMessage:
            def __init__(self, user_id, chat_id):
                self.from_user = type('obj', (object,), {'id': user_id})()
                self.chat = type('obj', (object,), {'id': chat_id})()
                self.text = "#админ"
        fake_msg = FakeMessage(call.from_user.id, call.message.chat.id)
        handle_admin_command(fake_msg, bot)
        bot.answer_callback_query(call.id)
