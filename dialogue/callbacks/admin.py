# ==========================================
# Файл: dialogue/callbacks/admin.py
# Справка: README.md → Обработчики кнопок / Админ
# Задача: обработка кнопок админ-меню
# Комментарий: логика добавления постов и диалога — в admin_commands.py
#              состояния — в message_dispatcher.py
# Зависит от: telebot, button_map, admin_commands, message_dispatcher
# Вызывается из: dialogue/callbacks/__init__.py
# ==========================================

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.button_map import get_text, get_callback, get_admin_menu_keyboard
from dialogue.publisher import add_publication
from dialogue.quotes import get_quotes_list, add_quote, set_quotes_interval, get_quotes_interval
from debug_utils import debug_log

# ==========================================
# РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ
# ==========================================
def register_admin_callbacks(bot, config):
    
    @bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
    def show_admin_panel(call):
        bot.edit_message_text(
            "🛡️ *Админ-панель*\n\nВыберите действие:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_admin_menu_keyboard(),
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    # ==========================================
    # КНОПКА «ДОБАВИТЬ ПОСТ» (вызов из admin_commands)
    # ==========================================
    @bot.callback_query_handler(func=lambda call: call.data == "add_post")
    def add_post_ui(call):
        from dialogue.admin_commands import show_add_post_ui
        show_add_post_ui(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == "cancel_add_post")
    def cancel_post(call):
        from dialogue.admin_commands import cancel_add_post
        cancel_add_post(call, bot)
    
    # ==========================================
    # УПРАВЛЕНИЕ ЦИТАТАМИ
    # ==========================================
    @bot.callback_query_handler(func=lambda call: call.data == "manage_quotes")
    def quotes_panel(call):
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(get_text("list_quotes"), callback_data=get_callback("list_quotes")),
            InlineKeyboardButton(get_text("add_quote"), callback_data=get_callback("add_quote")),
        )
        keyboard.add(
            InlineKeyboardButton(get_text("set_quote_interval"), callback_data=get_callback("set_quote_interval")),
            InlineKeyboardButton(get_text("back_to_admin"), callback_data=get_callback("back_to_admin")),
        )
        bot.edit_message_text(
            "📜 *Управление цитатами*\n\n"
            f"📊 Всего цитат: {len(get_quotes_list())}\n"
            f"⏱️ Интервал публикации: {get_quotes_interval()} мин.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "list_quotes")
    def list_quotes(call):
        quotes = get_quotes_list()
        if not quotes:
            bot.edit_message_text(
                "📭 База цитат пуста.\n\nДобавьте цитаты через #админ.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(get_text("back_to_admin"), callback_data=get_callback("back_to_admin"))
                )
            )
            return
        
        text = "📖 *Последние 20 цитат:*\n\n"
        for i, q in enumerate(quotes[-20:], 1):
            text += f"{i}. {q[:80]}{'...' if len(q) > 80 else ''}\n"
        
        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(get_text("back_to_admin"), callback_data=get_callback("back_to_admin"))
            ),
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "add_quote")
    def add_quote_ui(call):
        msg = bot.send_message(
            call.message.chat.id,
            "📜 *Добавление цитаты*\n\n"
            "Пришлите текст цитаты (можно на нескольких строках).\n"
            "Или /cancel для отмены.",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, process_new_quote, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "set_quote_interval")
    def set_interval_ui(call):
        msg = bot.send_message(
            call.message.chat.id,
            f"⏱️ *Текущий интервал цитат:* {get_quotes_interval()} мин.\n\n"
            "Введите новое значение в минутах (число от 5 до 720).\n"
            "Или /cancel для отмены.",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, process_quote_interval, bot)
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "back_to_admin")
    def back_to_admin(call):
        show_admin_panel(call)
    
    @bot.callback_query_handler(func=lambda call: call.data == "admin_logout")
    def admin_logout(call):
        from dialogue.admin_commands import logout_admin
        user_id = call.from_user.id
        logout_admin(user_id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.answer_callback_query(call.id, "👋 Вы вышли из админ-панели")
    
    # ==========================================
    # КНОПКА «ДИАЛОГ С АГЕНТОМ» (вызов из admin_commands)
    # ==========================================
    @bot.callback_query_handler(func=lambda call: call.data == "start_dialog")
    def start_dialog(call):
        from dialogue.admin_commands import show_dialog_ui
        show_dialog_ui(call, bot)

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (для цитат)
# ==========================================
def process_new_quote(message, bot):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Добавление цитаты отменено.", reply_markup=get_admin_menu_keyboard())
        return
    
    quote = message.text.strip()
    if add_quote(quote):
        bot.reply_to(message, "✅ Цитата добавлена в базу!", reply_markup=get_admin_menu_keyboard())
    else:
        bot.reply_to(message, "❌ Ошибка при сохранении цитаты.", reply_markup=get_admin_menu_keyboard())

def process_quote_interval(message, bot):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Изменение интервала отменено.", reply_markup=get_admin_menu_keyboard())
        return
    
    try:
        interval = int(message.text.strip())
        if interval < 5 or interval > 720:
            raise ValueError
        set_quotes_interval(interval)
        bot.reply_to(message, f"✅ Интервал цитат установлен на {interval} минут.", reply_markup=get_admin_menu_keyboard())
    except ValueError:
        bot.reply_to(message, "❌ Ошибка: введите число от 5 до 720.", reply_markup=get_admin_menu_keyboard())
