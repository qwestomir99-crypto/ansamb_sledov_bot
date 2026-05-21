# ==========================================
# Файл: dialogue/admin/callbacks.py
# Справка: README.md → Админка (обработчики кнопок)
# Задача: все handle_callback_* для режимов, пинга, цитат, диагностики и т.д.
# Комментарий: добавлены обработчики подменю (включая Диагностику)
# ==========================================

from dialogue.admin.auth import is_admin_authorized, log_admin_action
from dialogue.admin.menu import (
    get_admin_menu,
    get_modes_submenu,
    get_content_submenu,
    get_quotes_submenu,
    get_diagnostic_submenu
)
from dialogue.admin.quotes_admin import (
    handle_quotes_list,
    handle_quotes_add_start,
    handle_quotes_interval,
    handle_quotes_set_interval
)
from dialogue.admin.posts import (
    handle_pub_menu,
    ask_for_post_text,
    handle_vk_post
)
from dialogue.admin.diagnostics import handle_errors, handle_log, handle_debug
from dialogue.ping_modes import apply_ping_mode
from ping_utils import ping_self
import time

def handle_callback_mode(mode, bot, chat_id, message_id, user_id):
    from dialogue.admin_commands import load_config, save_config
    config = load_config()
    config["force_mode"] = mode
    config["force_mode_until"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_config(config)
    apply_ping_mode()
    log_admin_action(user_id, f"mode {mode}", "success")
    
    greetings = {
        "утро": "🌅 Доброе утро, сапёр. Сеть тлеет.",
        "день": "☀️ Хорошего дня. Не забывай #Тлеем.",
        "вечер": "🌙 Спокойного вечера. Наблюдение продолжается.",
        "ночь": "😴 Режим сна. Старший брат отдыхает."
    }
    
    bot.edit_message_text(
        f"✅ Режим «{mode}» установлен\n\n{greetings.get(mode, '')}",
        chat_id, message_id
    )
    from dialogue.admin_commands import return_to_admin_menu
    return_to_admin_menu(bot, chat_id, message_id, user_id)

def handle_callback_ping(interval, bot, chat_id, message_id, user_id):
    from dialogue.admin_commands import load_config, save_config
    config = load_config()
    if "ping" not in config:
        config["ping"] = {}
    config["ping"]["interval"] = interval
    save_config(config)
    apply_ping_mode()
    log_admin_action(user_id, f"ping {interval}", "success")
    bot.edit_message_text(f"✅ Пинг установлен на {interval} секунд", chat_id, message_id)
    from dialogue.admin_commands import return_to_admin_menu
    return_to_admin_menu(bot, chat_id, message_id, user_id)

def handle_callback_toggle_alisa(bot, chat_id, message_id, user_id):
    from dialogue.admin_commands import load_config, save_config
    config = load_config()
    if "alisa" not in config:
        config["alisa"] = {}
    config["alisa"]["enabled"] = not config["alisa"].get("enabled", True)
    save_config(config)
    
    new_status = "🟢 Старший брат: ВКЛ" if config["alisa"]["enabled"] else "🔴 Старший брат: ВЫКЛ"
    
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(row_width=2)
    brother_button = InlineKeyboardButton(new_status, callback_data="toggle_alisa")
    keyboard.add(
        InlineKeyboardButton("🎛 Режимы", callback_data="submenu_modes"),
        brother_button,
        InlineKeyboardButton("📝 Контент", callback_data="submenu_content"),
        InlineKeyboardButton("📜 Цитаты", callback_data="submenu_quotes"),
        InlineKeyboardButton("🔧 Диагностика", callback_data="submenu_diagnostic"),
        InlineKeyboardButton("🚪 Выйти", callback_data="logout")
    )
    
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)
    bot.answer_callback_query(call.id, f"Старший брат {'включён' if config['alisa']['enabled'] else 'выключен'}")

def register_callback_handlers(bot, config):
    """Регистрирует обработчики callback_query (нажатий на кнопки)"""

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

        # ---------- ПОДМЕНЮ ----------
        if data == "submenu_modes":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
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

        # ---------- НАСТРОЕНИЕ (обработчики кнопок) ----------
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
            handle_errors(user_id, bot, chat_id, message_id)
            return

        if data == "log":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_log(user_id, bot, chat_id, message_id)
            return

        # ---------- ДЕБАГ ----------
        if data == "debug":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_debug(user_id, bot, chat_id, message_id)
            return

        # ---------- ВЫХОД ----------
        if data == "logout":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            from dialogue.admin.auth import logout_admin
            logout_admin(user_id)
            log_admin_action(user_id, "logout", "success")
            bot.edit_message_text("🔓 Вы вышли из админ-панели", chat_id, message_id)
            return

        # ---------- ПУБЛИКАЦИИ ----------
        if data == "pub_menu":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_pub_menu(bot, chat_id, message_id, user_id)
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
            handle_vk_post(bot, chat_id, message_id, user_id)
            return

        # ---------- ЦИТАТЫ ----------
        if data == "quotes_list":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_quotes_list(bot, chat_id, message_id, user_id)
            return

        if data == "quotes_add":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_quotes_add_start(bot, chat_id, message_id, user_id)
            return

        if data == "quotes_interval":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_quotes_interval(bot, chat_id, message_id, user_id)
            return

        if data.startswith("quote_int_"):
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            interval = int(data.split("_")[2])
            handle_quotes_set_interval(interval, bot, chat_id, message_id, user_id)
            return

        # ---------- СТАРШИЙ БРАТ (прямой вызов из меню) ----------
        if data == "toggle_alisa":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_callback_toggle_alisa(bot, chat_id, message_id, user_id)
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
