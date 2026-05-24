# ==========================================
# Файл: dialogue/callbacks.py
# Справка: README.md → Обработчики кнопок
# Задача: обработка нажатий на инлайн-кнопки (callback_data)
# Комментарий: использует button_map.py для единого управления callback'ами
# Зависит от: telebot, button_map, admin_commands, quotes, publisher
# Вызывается из: bot.py (регистрация через register_callback_handlers)
# ==========================================

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================================
# ИМПОРТ МОДУЛЕЙ ПРОЕКТА
# ==========================================
from dialogue.button_map import get_callback, get_text, get_admin_menu_keyboard
from dialogue.admin_commands import (
    show_admin_panel, show_add_post_ui, show_vk_post_ui,
    show_quotes_panel, list_quotes, add_quote_ui, set_quote_interval_ui,
    show_diagnostics, admin_logout
)
from dialogue.user_settings import set_user_mood, get_moods_keyboard
from debug_utils import debug_log

# ==========================================
# ОСНОВНАЯ ФУНКЦИЯ РЕГИСТРАЦИИ
# ==========================================
def register_callback_handlers(bot, config):
    """
    Регистрирует все обработчики callback_data для инлайн-кнопок.
    Вызывается из bot.py при старте.
    """
    
    # ==========================================
    # 1. КНОПКИ АДМИН-МЕНЮ
    # ==========================================
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("manage_bot"))
    def callback_manage_bot(call):
        debug_log("CALLBACK", f"Админ-панель от {call.from_user.id}")
        show_admin_panel(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("add_post"))
    def callback_add_post(call):
        debug_log("CALLBACK", f"Добавление поста от {call.from_user.id}")
        show_add_post_ui(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("vk_post"))
    def callback_vk_post(call):
        debug_log("CALLBACK", f"Пост в VK от {call.from_user.id}")
        show_vk_post_ui(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("manage_quotes"))
    def callback_manage_quotes(call):
        debug_log("CALLBACK", f"Управление цитатами от {call.from_user.id}")
        show_quotes_panel(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("diagnostics"))
    def callback_diagnostics(call):
        debug_log("CALLBACK", f"Диагностика от {call.from_user.id}")
        show_diagnostics(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("logout"))
    def callback_logout(call):
        debug_log("CALLBACK", f"Выход админа {call.from_user.id}")
        admin_logout(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("back_to_admin"))
    def callback_back_to_admin(call):
        debug_log("CALLBACK", f"Назад в админ-меню от {call.from_user.id}")
        bot.edit_message_text(
            "🛡️ *Админ-панель*\n\nВыберите действие:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_admin_menu_keyboard(),
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("cancel"))
    def callback_cancel(call):
        debug_log("CALLBACK", f"Отмена от {call.from_user.id}")
        bot.edit_message_text(
            "❌ Действие отменено.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_admin_menu_keyboard()
        )
        bot.answer_callback_query(call.id)
    
    # ==========================================
    # 2. КНОПКИ УПРАВЛЕНИЯ ЦИТАТАМИ
    # ==========================================
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("list_quotes"))
    def callback_list_quotes(call):
        debug_log("CALLBACK", f"Список цитат от {call.from_user.id}")
        list_quotes(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("add_quote"))
    def callback_add_quote(call):
        debug_log("CALLBACK", f"Добавление цитаты от {call.from_user.id}")
        add_quote_ui(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("set_quote_interval"))
    def callback_set_quote_interval(call):
        debug_log("CALLBACK", f"Изменение интервала цитат от {call.from_user.id}")
        set_quote_interval_ui(call, bot)
    
    # ==========================================
    # 3. КНОПКИ РЕЖИМОВ (утро/день/вечер/ночь)
    # ==========================================
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("set_mode_morning"))
    def callback_mode_morning(call):
        debug_log("CALLBACK", f"Режим 'Утро' от {call.from_user.id}")
        from dialogue.activity_modes import set_mode
        set_mode("утро")
        bot.answer_callback_query(call.id, "🌅 Режим 'Утро' активирован")
        show_admin_panel(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("set_mode_day"))
    def callback_mode_day(call):
        debug_log("CALLBACK", f"Режим 'День' от {call.from_user.id}")
        from dialogue.activity_modes import set_mode
        set_mode("день")
        bot.answer_callback_query(call.id, "☀️ Режим 'День' активирован")
        show_admin_panel(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("set_mode_evening"))
    def callback_mode_evening(call):
        debug_log("CALLBACK", f"Режим 'Вечер' от {call.from_user.id}")
        from dialogue.activity_modes import set_mode
        set_mode("вечер")
        bot.answer_callback_query(call.id, "🌙 Режим 'Вечер' активирован")
        show_admin_panel(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("set_mode_night"))
    def callback_mode_night(call):
        debug_log("CALLBACK", f"Режим 'Ночь' от {call.from_user.id}")
        from dialogue.activity_modes import set_mode
        set_mode("ночь")
        bot.answer_callback_query(call.id, "🌌 Режим 'Ночь' активирован")
        show_admin_panel(call, bot)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("toggle_ping"))
    def callback_toggle_ping(call):
        debug_log("CALLBACK", f"Переключение пинга от {call.from_user.id}")
        from ping_utils import toggle_ping
        new_state = toggle_ping()
        bot.answer_callback_query(call.id, f"🔄 Пинг {'включён' if new_state else 'выключён'}")
        show_admin_panel(call, bot)
    
    # ==========================================
    # 4. КНОПКИ ДИАГНОСТИКИ
    # ==========================================
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("view_admin_log"))
    def callback_view_admin_log(call):
        debug_log("CALLBACK", f"Просмотр admin.log от {call.from_user.id}")
        from dialogue.admin.diagnostics import view_log
        view_log(call, bot, "admin")
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("view_error_log"))
    def callback_view_error_log(call):
        debug_log("CALLBACK", f"Просмотр error.log от {call.from_user.id}")
        from dialogue.admin.diagnostics import view_log
        view_log(call, bot, "error")
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("clear_logs"))
    def callback_clear_logs(call):
        debug_log("CALLBACK", f"Очистка логов от {call.from_user.id}")
        from dialogue.admin.diagnostics import clear_logs
        clear_logs(call, bot)
    
    # ==========================================
    # 5. ПОЛЬЗОВАТЕЛЬСКИЕ КНОПКИ
    # ==========================================
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("user_help"))
    def callback_user_help(call):
        debug_log("CALLBACK", f"Помощь пользователю {call.from_user.id}")
        bot.edit_message_text(
            "📖 *Справка*\n\n"
            "Доступные команды:\n"
            "• `#меню` — открыть меню\n"
            "• `#админ` — войти в админ-панель\n"
            "• `#говори <текст>` — спросить у Старшего брата\n"
            "• `#тлеем` — цитата\n"
            "• `#фиксируем` — подтверждение ритма\n"
            "• `#вспышка` — импульс\n"
            "• `#дышим` — пинг бота",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("user_tleem"))
    def callback_user_tleem(call):
        debug_log("CALLBACK", f"#тлеем от {call.from_user.id}")
        from dialogue.quotes import get_random_quote
        quote = get_random_quote()
        bot.edit_message_text(
            f"👁️ {quote}",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("user_fix"))
    def callback_user_fix(call):
        debug_log("CALLBACK", f"#фиксируем от {call.from_user.id}")
        bot.edit_message_text(
            "🔒 Фиксация принята. Ритм 0,8 Гц подтверждён.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == get_callback("user_flash"))
    def callback_user_flash(call):
        debug_log("CALLBACK", f"#вспышка от {call.from_user.id}")
        bot.edit_message_text(
            "⚡ Импульс зафиксирован. Синхронизация завершена. QSL.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    # ==========================================
    # 6. КНОПКИ НАСТРОЕНИЯ (из user_settings)
    # ==========================================
    
    @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("set_mood_"))
    def callback_set_mood(call):
        mood_id = call.data.replace("set_mood_", "")
        debug_log("CALLBACK", f"Установка настроения {mood_id} от {call.from_user.id}")
        set_user_mood(call.from_user.id, mood_id)
        bot.edit_message_text(
            f"✅ Настроение изменено.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "close_mood_menu")
    def callback_close_mood(call):
        debug_log("CALLBACK", f"Закрытие меню настроения от {call.from_user.id}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    # ==========================================
    # 7. ОБРАБОТЧИК НЕИЗВЕСТНЫХ CALLBACK
    # ==========================================
    
    @bot.callback_query_handler(func=lambda call: True)
    def callback_unknown(call):
        debug_log("CALLBACK", f"Неизвестный callback: {call.data} от {call.from_user.id}")
        bot.answer_callback_query(call.id, "⚠️ Кнопка не активна или устарела")
    
    debug_log("CALLBACKS", "✅ Все обработчики кнопок зарегистрированы")

# ==========================================
# КОНЕЦ ФАЙЛА
# ==========================================
