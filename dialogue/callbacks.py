# ==========================================
# Модуль: dialogue/callbacks.py
# Справка: README.md → Обработчики кнопок
# Задача: обработка callback_query (нажатий на кнопки)
# Комментарий: добавлены проверки, чтобы не редактировать сообщение тем же текстом (ошибка 400)
# Зависит от: admin_commands.py, help_menu.py, user_settings.py
# Вызывается из: bot.py
# ==========================================

from dialogue.admin_commands import (
    is_admin_authorized,
    handle_callback_mode, handle_callback_ping,
    handle_callback_errors, handle_callback_log,
    handle_callback_logout, handle_callback_pub_menu,
    handle_callback_toggle_alisa,
    handle_callback_quotes_list,
    handle_callback_quotes_add_start,
    handle_callback_quotes_interval,
    handle_callback_quotes_set_interval,
    handle_callback_vk_post,
    ask_for_post_text,
    get_admin_menu
)
from ping_utils import ping_self

def register_callback_handlers(bot, config):
    """Регистрирует обработчики кнопок (callback_query)"""

    # --- РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ СПРАВКИ ---
    try:
        from dialogue.help_menu import register_help_handlers
        register_help_handlers(bot)
        print("[CALLBACKS] Обработчики справки зарегистрированы")
    except ImportError as e:
        print(f"[CALLBACKS] Модуль help_menu не найден: {e}")

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        user_id = call.from_user.id
        data = call.data
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        # ---------- ВОЗВРАТ В АДМИН-МЕНЮ ----------
        if data == "admin_menu":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            bot.edit_message_text(
                "🛡️ Админ-меню:",
                chat_id, message_id,
                reply_markup=get_admin_menu()
            )
            bot.answer_callback_query(call.id)
            return

        # ---------- ПОДМЕНЮ (с проверкой на повтор) ----------
        if data == "submenu_modes":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            from dialogue.admin_commands import get_modes_submenu
            new_text = "🎛 *Управление режимами и пингом:*"
            if call.message.text != new_text:
                bot.edit_message_text(
                    new_text,
                    chat_id, message_id,
                    parse_mode='Markdown',
                    reply_markup=get_modes_submenu()
                )
            else:
                bot.answer_callback_query(call.id, "Уже в меню режимов")
            return

        if data == "submenu_content":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            from dialogue.admin_commands import get_content_submenu
            new_text = "📝 *Управление контентом:*"
            if call.message.text != new_text:
                bot.edit_message_text(
                    new_text,
                    chat_id, message_id,
                    parse_mode='Markdown',
                    reply_markup=get_content_submenu()
                )
            else:
                bot.answer_callback_query(call.id, "Уже в меню контента")
            return

        if data == "submenu_quotes":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            from dialogue.admin_commands import get_quotes_submenu
            new_text = "📜 *Управление цитатами:*"
            if call.message.text != new_text:
                bot.edit_message_text(
                    new_text,
                    chat_id, message_id,
                    parse_mode='Markdown',
                    reply_markup=get_quotes_submenu()
                )
            else:
                bot.answer_callback_query(call.id, "Уже в меню цитат")
            return

        if data == "submenu_diagnostic":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            from dialogue.admin_commands import get_diagnostic_submenu
            new_text = "🔧 *Диагностика:*"
            if call.message.text != new_text:
                bot.edit_message_text(
                    new_text,
                    chat_id, message_id,
                    parse_mode='Markdown',
                    reply_markup=get_diagnostic_submenu()
                )
            else:
                bot.answer_callback_query(call.id, "Уже в меню диагностики")
            return

        # ---------- НАСТРОЕНИЕ ----------
        if data.startswith("set_mood_"):
            mood_id = data.replace("set_mood_", "")
            try:
                from dialogue.user_settings import set_user_mood, MOODS
                if mood_id in MOODS:
                    set_user_mood(user_id, mood_id)
                    bot.answer_callback_query(
                        call.id, 
                        f"✅ Настроение «{MOODS[mood_id]['name']}» установлено"
                    )
                    bot.edit_message_text(
                        f"🎭 Настроение изменено на *{MOODS[mood_id]['name']}*",
                        chat_id, message_id,
                        parse_mode='Markdown'
                    )
                else:
                    bot.answer_callback_query(call.id, "❌ Ошибка: настроение не найдено")
            except ImportError:
                bot.answer_callback_query(call.id, "❌ Модуль настроений не загружен")
            return

        if data == "close_mood_menu":
            bot.delete_message(chat_id, message_id)
            bot.answer_callback_query(call.id, "Меню закрыто")
            return

        # ---------- РЕЖИМЫ ----------
        if data.startswith("mode_"):
            mode = data.split("_")[1]
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_mode(mode, bot, chat_id, message_id, user_id)
            return

        # ---------- ПИНГ ----------
        if data.startswith("ping_"):
            interval = int(data.split("_")[1])
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_ping(interval, bot, chat_id, message_id, user_id)
            return

        # ---------- ОШИБКИ И ЛОГ ----------
        if data == "errors":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_errors(user_id, bot, chat_id, message_id)
            return

        if data == "log":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_log(user_id, bot, chat_id, message_id)
            return

        # ---------- ВЫХОД ----------
        if data == "logout":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_logout(user_id, bot, chat_id, message_id)
            return

        # ---------- ПУБЛИКАЦИИ ----------
        if data == "pub_menu":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_pub_menu(bot, chat_id, message_id, user_id)
            return

        if data == "add_post":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            ask_for_post_text(bot, chat_id, message_id)
            return

        # ---------- ПОСТ В VK ----------
        if data == "vk_post":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_vk_post(bot, chat_id, message_id, user_id)
            return

        # ---------- СТАРШИЙ БРАТ ----------
        if data == "toggle_alisa":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_toggle_alisa(bot, chat_id, message_id, user_id)
            return

        # ---------- ЦИТАТЫ ----------
        if data == "quotes_list":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_quotes_list(bot, chat_id, message_id, user_id)
            return

        if data == "quotes_add":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_quotes_add_start(bot, chat_id, message_id, user_id)
            return

        if data == "quotes_interval":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_quotes_interval(bot, chat_id, message_id, user_id)
            return

        if data.startswith("quote_int_"):
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            interval = int(data.split("_")[2])
            handle_callback_quotes_set_interval(interval, bot, chat_id, message_id, user_id)
            return

        # ---------- СПРАВКА: НАЗАД ----------
        if data == "help_back":
            from dialogue.help_menu import get_help_keyboard
            new_text = "📖 *Справка по командам*\n\nВыберите команду для подробного описания:"
            if call.message.text != new_text:
                bot.edit_message_text(
                    new_text,
                    chat_id, message_id,
                    parse_mode='Markdown',
                    reply_markup=get_help_keyboard()
                )
            else:
                bot.answer_callback_query(call.id, "Уже в главном меню справки")
            return

        # ---------- ПОЛЬЗОВАТЕЛЬСКИЕ КНОПКИ ----------
        if data == "tleem":
            bot.send_message(chat_id, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет. Ожидаем #Фиксируем.")
        elif data == "fixiruem":
            bot.send_message(chat_id, "🔒 Фиксация принята. Ритм 0,8 Гц подтверждён. Сеть тлеет.")
        elif data == "vspishka":
            bot.send_message(chat_id, "💥 Импульс зафиксирован. Синхронизация завершена. QSL.")
        elif data == "dyshim":
            ping_self()
            bot.send_message(chat_id, "🌬 Пинг отправлен (бот не отвечает)")
        elif data == "govorim":
            bot.send_message(chat_id, "🗣 Напиши #говори <текст> в чат")
        elif data == "help":
            help_text = """
📖 *Доступные хештеги:*

🔹 *#тлеем* — разлом
🔹 *#фиксируем* — синхронизация
🔹 *#вспышка* — импульс
🔹 *#дышим* — пинг
🔹 *#говори <текст>* — вопрос Старшему брату
🔹 *#меню* — меню
🔹 *#* — интерактивная справка
            """
            bot.send_message(chat_id, help_text, parse_mode='Markdown')
        else:
            bot.answer_callback_query(call.id)

        bot.answer_callback_query(call.id)
