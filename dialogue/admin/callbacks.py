# ==========================================
# Файл: dialogue/admin/callbacks.py
# Задача: диспетчеризация callback_query (нажатий на кнопки)
# Комментарий: вся логика вынесена в модули, здесь только маршрутизация и уведомления
# ==========================================

import os
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.admin.auth import is_admin_authorized, log_admin_action
from dialogue.admin.menu import (
    get_admin_menu, get_modes_submenu, get_adaptive_submenu,
    get_content_submenu, get_quotes_submenu, get_diagnostic_submenu, get_debugger_menu
)
from dialogue.admin.quotes_admin import handle_quotes_list, handle_quotes_add_start, handle_quotes_interval, handle_quotes_set_interval
from dialogue.admin.posts import handle_pub_menu, ask_for_post_text, handle_vk_post
from dialogue.ping_modes import apply_ping_mode
from ping_utils import ping_self
from debug_utils import load_config as load_debug_config, save_config as save_debug_config

ADAPTIVE_CONFIG_FILE = "dialogue/data/adaptive_config.json"

def _load_adaptive():
    if not os.path.exists(ADAPTIVE_CONFIG_FILE): return {"enabled": False}
    try:
        with open(ADAPTIVE_CONFIG_FILE, "r") as f: return json.load(f)
    except: return {"enabled": False}

def _save_adaptive(config):
    os.makedirs(os.path.dirname(ADAPTIVE_CONFIG_FILE), exist_ok=True)
    with open(ADAPTIVE_CONFIG_FILE, "w") as f: json.dump(config, f, indent=2)

def register_callback_handlers(bot, config):

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        uid, data, cid, mid = call.from_user.id, call.data, call.message.chat.id, call.message.message_id

        if not is_admin_authorized(uid) and data not in ["tleem", "fixiruem", "vspishka", "dyshim", "govorim", "help"]:
            bot.answer_callback_query(call.id, "❌ Не авторизован")
            return

        # --- Админ-меню ---
        if data == "admin_menu":
            bot.edit_message_text("🛡️ Админ-меню:", cid, mid, reply_markup=get_admin_menu())
            bot.answer_callback_query(call.id, "📍 Главное меню")

        # --- Подменю ---
        elif data == "submenu_modes":
            bot.edit_message_text("🎛 *Управление режимами и пингом:*", cid, mid, parse_mode='Markdown', reply_markup=get_modes_submenu())
            bot.answer_callback_query(call.id, "🎛 Режимы")
        elif data == "submenu_adaptive":
            status = "✅ Включены" if _load_adaptive().get("enabled") else "❌ Отключены"
            bot.edit_message_text(f"🧠 *Адаптивные режимы*\n\nСтатус: {status}", cid, mid, parse_mode='Markdown', reply_markup=get_adaptive_submenu())
            bot.answer_callback_query(call.id, "🧠 Адаптивные режимы")
        elif data == "submenu_content":
            bot.edit_message_text("📝 *Управление контентом:*", cid, mid, parse_mode='Markdown', reply_markup=get_content_submenu())
            bot.answer_callback_query(call.id, "📝 Контент")
        elif data == "submenu_quotes":
            bot.edit_message_text("📜 *Управление цитатами:*", cid, mid, parse_mode='Markdown', reply_markup=get_quotes_submenu())
            bot.answer_callback_query(call.id, "📜 Цитаты")
        elif data == "submenu_diagnostic":
            bot.edit_message_text("🔧 *Диагностика:*", cid, mid, parse_mode='Markdown', reply_markup=get_diagnostic_submenu())
            bot.answer_callback_query(call.id, "🔧 Диагностика")

        # --- Шаббат ---
        elif data == "shabbat_info":
            from dialogue.shabbat_manager import is_shabbat, fetch_shabbat_times, get_coordinates
            lat, lon = get_coordinates()
            start, end = fetch_shabbat_times(lat, lon)
            text = f"📍 {lat}, {lon}\n"
            if start and end: text += f"🕯 {start.strftime('%Y-%m-%d %H:%M')} → ✨ {end.strftime('%Y-%m-%d %H:%M')}\n"
            text += f"📌 Шаббат: {'✅ ДА' if is_shabbat() else '❌ НЕТ'}"
            bot.edit_message_text(text, cid, mid)
            bot.answer_callback_query(call.id, "🕯 Шаббат")

        # --- Режимы ---
        elif data.startswith("mode_"):
            mode = data.split("_")[1]
            emojis = {"утро": "🌅", "день": "☀️", "вечер": "🌙", "ночь": "🌌"}
            bot.answer_callback_query(call.id, f"{emojis.get(mode, '')} Режим «{mode}»")
            from dialogue.admin_commands import load_config, save_config, return_to_admin_menu
            cfg = load_config()
            cfg["force_mode"] = mode
            cfg["force_mode_until"] = __import__('time').strftime("%Y-%m-%d %H:%M:%S")
            save_config(cfg)
            apply_ping_mode()
            greetings = {"утро": "🌅 Доброе утро, сапёр.", "день": "☀️ Хорошего дня.", "вечер": "🌙 Спокойного вечера.", "ночь": "😴 Режим сна."}
            bot.edit_message_text(f"✅ Режим «{mode}»\n\n{greetings.get(mode, '')}", cid, mid)
            return_to_admin_menu(bot, cid, mid, uid)

        # --- Пинг ---
        elif data.startswith("ping_"):
            interval = int(data.split("_")[1])
            bot.answer_callback_query(call.id, f"🔄 Пинг {interval} сек")
            from dialogue.admin_commands import load_config, save_config, return_to_admin_menu
            cfg = load_config()
            cfg.setdefault("ping", {})["interval"] = interval
            save_config(cfg)
            apply_ping_mode()
            bot.edit_message_text(f"✅ Пинг {interval} сек", cid, mid)
            return_to_admin_menu(bot, cid, mid, uid)

        # --- Старший брат ---
        elif data in ["toggle_alisa_on", "toggle_alisa_off"]:
            enabled = data == "toggle_alisa_on"
            bot.answer_callback_query(call.id, f"{'✅' if enabled else '❌'} Старший брат {'включён' if enabled else 'выключен'}")
            from dialogue.admin_commands import load_config, save_config, return_to_admin_menu
            cfg = load_config()
            cfg.setdefault("alisa", {})["enabled"] = enabled
            save_config(cfg)
            bot.edit_message_text(f"{'✅' if enabled else '❌'} Старший брат {'включён' if enabled else 'выключен'}", cid, mid)
            return_to_admin_menu(bot, cid, mid, uid)

        # --- Адаптивные ---
        elif data == "adaptive_enable":
            cfg = _load_adaptive(); cfg["enabled"] = True; _save_adaptive(cfg)
            try: from dialogue.adaptive_modes import set_adaptive_enabled; set_adaptive_enabled(True)
            except: pass
            bot.edit_message_text("✅ Адаптивные режимы включены", cid, mid)
            bot.answer_callback_query(call.id, "✅ Адаптивные режимы включены")
        elif data == "adaptive_disable":
            cfg = _load_adaptive(); cfg["enabled"] = False; _save_adaptive(cfg)
            try: from dialogue.adaptive_modes import set_adaptive_enabled; set_adaptive_enabled(False)
            except: pass
            bot.edit_message_text("❌ Адаптивные режимы выключены", cid, mid)
            bot.answer_callback_query(call.id, "❌ Адаптивные режимы выключены")
        elif data == "adaptive_reset":
            try: from dialogue.adaptive_modes import reset_to_etalon; reset_to_etalon()
            except: pass
            bot.edit_message_text("📊 Сброшено к эталону", cid, mid)
            bot.answer_callback_query(call.id, "📊 Сброшено к эталону")

        # --- Дебаггер ---
        elif data == "debugger_menu":
            bot.edit_message_text("🐞 *Управление дебаггером*", cid, mid, parse_mode='Markdown', reply_markup=get_debugger_menu())
            bot.answer_callback_query(call.id, "🐞 Дебаггер")
        elif data == "debugger_enable":
            cfg = load_debug_config(); cfg["enabled"] = True; save_debug_config(cfg)
            bot.edit_message_reply_markup(cid, mid, reply_markup=get_debugger_menu())
            bot.answer_callback_query(call.id, "✅ Дебаггер включён")
        elif data == "debugger_disable":
            cfg = load_debug_config(); cfg["enabled"] = False; save_debug_config(cfg)
            bot.edit_message_reply_markup(cid, mid, reply_markup=get_debugger_menu())
            bot.answer_callback_query(call.id, "🔴 Дебаггер выключен")
        elif data == "debugger_interval":
            kb = InlineKeyboardMarkup(row_width=3)
            for i in [0, 1, 5, 10, 30]: kb.add(InlineKeyboardButton("сразу" if i == 0 else f"{i} мин", callback_data=f"debugger_set_interval_{i}"))
            kb.add(InlineKeyboardButton("◀️ Назад", callback_data="debugger_menu"))
            bot.edit_message_text("⏱ *Интервал отправки логов*", cid, mid, parse_mode='Markdown', reply_markup=kb)
            bot.answer_callback_query(call.id, "⏱ Интервал")
        elif data.startswith("debugger_set_interval_"):
            interval = int(data.split("_")[-1])
            cfg = load_debug_config(); cfg["interval_minutes"] = interval; save_debug_config(cfg)
            bot.edit_message_reply_markup(cid, mid, reply_markup=get_debugger_menu())
            bot.answer_callback_query(call.id, f"✅ {'Сразу' if interval == 0 else f'{interval} мин'}")
        elif data == "debugger_toggle_send":
            cfg = load_debug_config(); cfg["send_to_telegram"] = not cfg.get("send_to_telegram", True); save_debug_config(cfg)
            bot.edit_message_reply_markup(cid, mid, reply_markup=get_debugger_menu())
            bot.answer_callback_query(call.id, f"📨 TG: {'вкл' if cfg['send_to_telegram'] else 'выкл'}")
        elif data == "debugger_modules":
            cfg = load_debug_config(); current = cfg.get("modules", [])
            mods = ["AUTOPOSTER", "VK_UPLOADER", "VK_READER", "QUOTES", "PUBLISHER", "HANDLERS", "POSTS", "AGENT"]
            kb = InlineKeyboardMarkup(row_width=2)
            for m in mods: kb.add(InlineKeyboardButton(f"{'✅' if m in current else '⬜'} {m}", callback_data=f"debugger_toggle_module_{m}"))
            kb.add(InlineKeyboardButton("◀️ Назад", callback_data="debugger_menu"))
            bot.edit_message_text("📋 *Модули*", cid, mid, parse_mode='Markdown', reply_markup=kb)
            bot.answer_callback_query(call.id, "📋 Модули")
        elif data.startswith("debugger_toggle_module_"):
            module = data.replace("debugger_toggle_module_", "")
            cfg = load_debug_config(); modules = cfg.get("modules", [])
            if module in modules: modules.remove(module); bot.answer_callback_query(call.id, f"⬜ {module}")
            else: modules.append(module); bot.answer_callback_query(call.id, f"✅ {module}")
            cfg["modules"] = modules; save_debug_config(cfg)
            current = cfg.get("modules", [])
            mods = ["AUTOPOSTER", "VK_UPLOADER", "VK_READER", "QUOTES", "PUBLISHER", "HANDLERS", "POSTS", "AGENT"]
            kb = InlineKeyboardMarkup(row_width=2)
            for m in mods: kb.add(InlineKeyboardButton(f"{'✅' if m in current else '⬜'} {m}", callback_data=f"debugger_toggle_module_{m}"))
            kb.add(InlineKeyboardButton("◀️ Назад", callback_data="debugger_menu"))
            bot.edit_message_reply_markup(cid, mid, reply_markup=kb)
        elif data == "debugger_logs":
            if os.path.exists("debug.log"):
                with open("debug.log", "r", encoding="utf-8") as f: lines = f.readlines()
                log_text = "".join(lines[-50:])
                if log_text.strip():
                    for i in range(0, len(log_text), 4000): bot.send_message(uid, f"```\n{log_text[i:i+4000]}\n```", parse_mode='Markdown')
                    bot.edit_message_text("✅ Логи в личку", cid, mid)
                else: bot.edit_message_text("📭 Логи пусты", cid, mid)
            else: bot.edit_message_text("📭 debug.log не найден", cid, mid)
            bot.answer_callback_query(call.id, "📋 Логи")

        # --- Настроение ---
        elif data.startswith("set_mood_"):
            mood_id = data.replace("set_mood_", "")
            try:
                from dialogue.user_settings import set_user_mood, MOODS
                if mood_id in MOODS:
                    set_user_mood(uid, mood_id)
                    bot.edit_message_text(f"🎭 Настроение: *{MOODS[mood_id]['name']}*", cid, mid, parse_mode='Markdown')
                    bot.answer_callback_query(call.id, f"✅ {MOODS[mood_id]['emoji']} {MOODS[mood_id]['name']}")
            except ImportError: bot.answer_callback_query(call.id, "❌ Модуль не загружен")
        elif data == "close_mood_menu":
            bot.delete_message(cid, mid)
            bot.answer_callback_query(call.id, "✅ Меню закрыто")

        # --- Выход ---
        elif data == "logout":
            from dialogue.admin.auth import logout_admin
            logout_admin(uid)
            bot.edit_message_text("🔓 Вы вышли из админ-панели", cid, mid)
            bot.answer_callback_query(call.id, "👋 До встречи, сапёр")

        # --- Публикации ---
        elif data == "pub_menu":
            bot.answer_callback_query(call.id, "📝 Публикации")
            handle_pub_menu(bot, cid, mid, uid)
        elif data == "add_post":
            bot.answer_callback_query(call.id, "📝 Новый пост")
            ask_for_post_text(bot, cid, mid)
        elif data == "vk_post":
            bot.answer_callback_query(call.id, "📘 Пост в VK")
            handle_vk_post(bot, cid, mid, uid)

        # --- Цитаты ---
        elif data == "quotes_list":
            bot.answer_callback_query(call.id, "📜 Список цитат")
            handle_quotes_list(bot, cid, mid, uid)
        elif data == "quotes_add":
            bot.answer_callback_query(call.id, "➕ Новая цитата")
            handle_quotes_add_start(bot, cid, mid, uid)
        elif data == "quotes_interval":
            bot.answer_callback_query(call.id, "⏱ Интервал цитат")
            handle_quotes_interval(bot, cid, mid, uid)
        elif data.startswith("quote_int_"):
            interval = int(data.split("_")[2])
            bot.answer_callback_query(call.id, f"⏱ {interval} мин")
            handle_quotes_set_interval(interval, bot, cid, mid, uid)

        # --- Пользовательские ---
        elif data == "tleem":
            bot.send_message(cid, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет.")
            bot.answer_callback_query(call.id, "💥 #Тлеем")
        elif data == "fixiruem":
            bot.send_message(cid, "🔒 Фиксация принята. Сеть тлеет.")
            bot.answer_callback_query(call.id, "🔒 #Фиксируем")
        elif data == "vspishka":
            bot.send_message(cid, "💥 Импульс зафиксирован. QSL.")
            bot.answer_callback_query(call.id, "💥 #Вспышка")
        elif data == "dyshim":
            ping_self(); bot.send_message(cid, "🌬 Пинг отправлен")
            bot.answer_callback_query(call.id, "🌬 #Дышим")
        elif data == "govorim":
            bot.send_message(cid, "🗣 Напиши #говори <текст>")
            bot.answer_callback_query(call.id, "🗣 #Говорим")
        elif data == "help":
            bot.send_message(cid, "📖 #тлеем | #фиксируем | #вспышка | #дышим | #говори | #меню", parse_mode='Markdown')
            bot.answer_callback_query(call.id, "📖 Справка")
        else:
            bot.answer_callback_query(call.id)
