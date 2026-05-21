# ==========================================
# Файл: new_debugger/dialogue/admin/callbacks.py
# Справка: README.md → Админка (обработчики кнопок)
# Задача: обработка callback_query (нажатий на кнопки)
# Комментарий: добавлены обработчики для дебаггера и Шаббата
# ==========================================

import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.admin.auth import is_admin_authorized, log_admin_action
from dialogue.admin.menu import (
    get_admin_menu,
    get_modes_submenu,
    get_content_submenu,
    get_quotes_submenu,
    get_diagnostic_submenu,
    get_debugger_menu
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
from debug_utils import load_config as load_debug_config, save_config as save_debug_config

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
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    brother_button = InlineKeyboardButton(new_status, callback_data="toggle_alisa")
    keyboard.add(
        InlineKeyboardButton("🎛 Режимы", callback_data="submenu_modes"),
        brother_button,
        InlineKeyboardButton("📝 Контент", callback_data="submenu_content"),
        InlineKeyboardButton("📜 Цитаты", callback_data="submenu_quotes"),
        InlineKeyboardButton("🔧 Диагностика", callback_data="submenu_diagnostic"),
        InlineKeyboardButton("🐞 Дебаггер", callback_data="debugger_menu"),
        InlineKeyboardButton("🚪 Выйти", callback_data="logout")
    )
    
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)
    bot.answer_callback_query(call.id, f"Старший брат {'включён' if config['alisa']['enabled'] else 'выключен'}")

# ==========================================
# Обработчики дебаггера
# ==========================================

def handle_debugger_enable(bot, chat_id, message_id, user_id):
    config = load_debug_config()
    config["enabled"] = True
    save_debug_config(config)
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=get_debugger_menu())
    bot.answer_callback_query(call.id, "✅ Дебаггер включён")

def handle_debugger_disable(bot, chat_id, message_id, user_id):
    config = load_debug_config()
    config["enabled"] = False
    save_debug_config(config)
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=get_debugger_menu())
    bot.answer_callback_query(call.id, "🔴 Дебаггер выключен")

def handle_debugger_interval(bot, chat_id, message_id, user_id):
    """Показывает меню выбора интервала"""
    keyboard = InlineKeyboardMarkup(row_width=3)
    for interval in [0, 1, 5, 10, 30]:
        text = "сразу" if interval == 0 else f"{interval} мин"
        keyboard.add(InlineKeyboardButton(text, callback_data=f"debugger_set_interval_{interval}"))
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="debugger_menu"))
    bot.edit_message_text(
        "⏱ *Интервал отправки логов*\n\n"
        "• 0 = отправлять сразу каждый лог\n"
        "• 1, 5, 10, 30 = накопление и отправка пачкой",
        chat_id, message_id,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    bot.answer_callback_query(call.id)

def handle_debugger_set_interval(interval, bot, chat_id, message_id, user_id):
    config = load_debug_config()
    config["interval_minutes"] = interval
    save_debug_config(config)
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=get_debugger_menu())
    text = "сразу" if interval == 0 else f"каждые {interval} мин"
    bot.answer_callback_query(call.id, f"Интервал установлен: {text}")

def handle_debugger_toggle_send(bot, chat_id, message_id, user_id):
    config = load_debug_config()
    config["send_to_telegram"] = not config.get("send_to_telegram", True)
    save_debug_config(config)
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=get_debugger_menu())
    status = "включена" if config["send_to_telegram"] else "выключена"
    bot.answer_callback_query(call.id, f"Отправка в Telegram {status}")

def handle_debugger_modules(bot, chat_id, message_id, user_id):
    """Показывает список модулей для выбора"""
    config = load_debug_config()
    current_modules = config.get("modules", [])
    
    modules_list = [
        "AUTOPOSTER", "VK_UPLOADER", "VK_READER", "QUOTES",
        "PUBLISHER", "HANDLERS", "POSTS", "AGENT"
    ]
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    for module in modules_list:
        marker = "✅ " if module in current_modules else "⬜ "
        keyboard.add(InlineKeyboardButton(f"{marker}{module}", callback_data=f"debugger_toggle_module_{module}"))
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="debugger_menu"))
    
    bot.edit_message_text(
        "📋 *Выбери модули для логирования*\n\n"
        "✅ = логировать, ⬜ = не логировать\n\n"
        "Пустой список = логировать все модули",
        chat_id, message_id,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    bot.answer_callback_query(call.id)

def handle_debugger_toggle_module(module, bot, chat_id, message_id, user_id):
    config = load_debug_config()
    modules = config.get("modules", [])
    if module in modules:
        modules.remove(module)
    else:
        modules.append(module)
    config["modules"] = modules
    save_debug_config(config)
    handle_debugger_modules(bot, chat_id, message_id, user_id)

def handle_debugger_logs(bot, chat_id, message_id, user_id):
    """Отправляет последние логи из буфера или файла"""
    logs_file = "debug.log"
    if os.path.exists(logs_file):
        try:
            with open(logs_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            last_lines = lines[-50:] if len(lines) > 50 else lines
            log_text = "".join(last_lines)
            if log_text.strip():
                for i in range(0, len(log_text), 4000):
                    bot.send_message(user_id, f"```\n{log_text[i:i+4000]}\n```", parse_mode='Markdown')
                bot.edit_message_text("✅ Логи отправлены в личку", chat_id, message_id)
            else:
                bot.edit_message_text("📭 Логи пусты", chat_id, message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Ошибка чтения: {e}", chat_id, message_id)
    else:
        bot.edit_message_text("📭 Файл debug.log не найден", chat_id, message_id)
    bot.answer_callback_query(call.id)

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

        # ---------- ШАББАТ (информация) ----------
        if data == "shabbat_info":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            from dialogue.shabbat_manager import is_shabbat, fetch_shabbat_times, get_coordinates
            lat, lon = get_coordinates()
            start, end = fetch_shabbat_times(lat, lon)
            shabbat_now = is_shabbat()
            text = f"📍 *Координаты:* {lat}, {lon}\n"
            if start and end:
                text += f"🕯 *Начало Шаббата:* {start.strftime('%Y-%m-%d %H:%M')}\n"
                text += f"✨ *Окончание:* {end.strftime('%Y-%m-%d %H:%M')}\n"
            text += f"📌 *Сейчас Шаббат:* {'✅ ДА' if shabbat_now else '❌ НЕТ'}\n"
            text += f"⏚ *Ритм 0,8 Гц стабилен.*"
            bot.edit_message_text(text, chat_id, message_id, parse_mode='Markdown')
            bot.answer_callback_query(call.id)
            return

        # ---------- ДЕБАГГЕР ----------
        if data == "debugger_menu":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            bot.edit_message_text(
                "🐞 *Управление дебаггером*",
                chat_id, message_id,
                parse_mode='Markdown',
                reply_markup=get_debugger_menu()
            )
            bot.answer_callback_query(call.id)
            return

        if data == "debugger_enable":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_debugger_enable(bot, chat_id, message_id, user_id)
            return

        if data == "debugger_disable":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_debugger_disable(bot, chat_id, message_id, user_id)
            return

        if data == "debugger_interval":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_debugger_interval(bot, chat_id, message_id, user_id)
            return

        if data.startswith("debugger_set_interval_"):
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            interval = int(data.split("_")[-1])
            handle_debugger_set_interval(interval, bot, chat_id, message_id, user_id)
            return

        if data == "debugger_toggle_send":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_debugger_toggle_send(bot, chat_id, message_id, user_id)
            return

        if data == "debugger_modules":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_debugger_modules(bot, chat_id, message_id, user_id)
            return

        if data.startswith("debugger_toggle_module_"):
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            module = data.replace("debugger_toggle_module_", "")
            handle_debugger_toggle_module(module, bot, chat_id, message_id, user_id)
            return

        if data == "debugger_logs":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_debugger_logs(bot, chat_id, message_id, user_id)
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
            handle_errors(user_id, bot, chat_id, message_id)
            return

        if data == "log":
            if not is_admin_authorized(user_id):
                bot.answer_callback_query(call.id, "❌ Не авторизован")
                return
            handle_log(user_id, bot, chat_id, message_id)
            return

        # ---------- ДЕБАГ (старая кнопка) ----------
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

        # ---------- СТАРШИЙ БРАТ ----------
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
