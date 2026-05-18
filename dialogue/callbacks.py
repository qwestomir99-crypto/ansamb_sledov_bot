# ==========================================
# Модуль: dialogue/callbacks.py
# Справка: README.md → Обработчики кнопок
# Задача: обработка callback_query (нажатий на кнопки)
# Комментарий: добавлена кнопка "🎬 Пост в VK (с медиа)"
# Зависит от: admin_commands.py
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

        # ---------- РЕЖИМЫ ----------
        if data.startswith("mode_"):
            mode = data.split("_")[1]
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован. Введите #админ <пароль>")
                return
            handle_callback_mode(mode, bot, chat_id, message_id, user_id)

        # ---------- ПИНГ ----------
        elif data.startswith("ping_"):
            interval = int(data.split("_")[1])
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован. Введите #админ <пароль>")
                return
            handle_callback_ping(interval, bot, chat_id, message_id, user_id)

        # ---------- ОШИБКИ И ЛОГ ----------
        elif data == "errors":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован. Введите #админ <пароль>")
                return
            handle_callback_errors(user_id, bot, chat_id, message_id)

        elif data == "log":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован. Введите #админ <пароль>")
                return
            handle_callback_log(user_id, bot, chat_id, message_id)

        # ---------- ВЫХОД ----------
        elif data == "logout":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_logout(user_id, bot, chat_id, message_id)

        # ---------- ПУБЛИКАЦИИ ----------
        elif data == "pub_menu":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_pub_menu(bot, chat_id, message_id, user_id)

        elif data == "add_post":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            ask_for_post_text(bot, chat_id, message_id)

        # ---------- ПОСТ В VK (НОВЫЙ) ----------
        elif data == "vk_post":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_vk_post(bot, chat_id, message_id, user_id)

        # ---------- АЛИСА ----------
        elif data == "toggle_alisa":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_toggle_alisa(bot, chat_id, message_id, user_id)

        # ---------- ЦИТАТЫ ----------
        elif data == "quotes_list":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_quotes_list(bot, chat_id, message_id, user_id)

        elif data == "quotes_add":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_quotes_add_start(bot, chat_id, message_id, user_id)

        elif data == "quotes_interval":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_quotes_interval(bot, chat_id, message_id, user_id)

        elif data.startswith("quote_int_"):
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            interval = int(data.split("_")[2])
            handle_callback_quotes_set_interval(interval, bot, chat_id, message_id, user_id)

        # ---------- ПОЛЬЗОВАТЕЛЬСКИЕ КНОПКИ ----------
        elif data == "tleem":
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
            """
            bot.send_message(chat_id, help_text, parse_mode='Markdown')

        else:
            # Неизвестный callback — просто отвечаем
            bot.answer_callback_query(call.id)

        bot.answer_callback_query(call.id)
