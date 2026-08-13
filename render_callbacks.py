# ==========================================
# Файл: render_callbacks.py (для Render)
# Справка: README.md → Telegram прокси / Render / Кнопки
# Задача: обработчики текстовых команд и callback'ов на Render
# Комментарий: вызывается из bot.py на Render. Все команды и кнопки здесь.
# Зависит от: telebot, requests
# Вызывается из: bot.py (Render)
# Версия: 2.0 — добавлена обработка текстовых команд
# ==========================================

import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

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

def get_admin_buttons():
    """Кнопки админ-меню"""
    return [
        [{"text": "🤖 Управление ботом", "callback_data": "submenu_modes"},
         {"text": "🧠 Адаптивные режимы", "callback_data": "submenu_adaptive"}],
        [{"text": "📝 Публикации", "callback_data": "submenu_content"},
         {"text": "➕ Добавить пост", "callback_data": "add_post"}],
        [{"text": "🎬 Пост в VK", "callback_data": "vk_post"},
         {"text": "📜 Цитаты", "callback_data": "submenu_quotes"}],
        [{"text": "🔧 Диагностика", "callback_data": "submenu_diagnostic"},
         {"text": "🐞 Дебаггер", "callback_data": "debugger_menu"}],
        [{"text": "🚪 Выйти", "callback_data": "logout"}]
    ]

def get_modes_buttons():
    """Кнопки режимов"""
    return [
        [{"text": "🌅 Утро", "callback_data": "mode_утро"},
         {"text": "☀️ День", "callback_data": "mode_день"}],
        [{"text": "🌙 Вечер", "callback_data": "mode_вечер"},
         {"text": "🌌 Ночь", "callback_data": "mode_ночь"}],
        [{"text": "◀️ Назад", "callback_data": "admin_menu"}]
    ]

def get_quotes_buttons():
    """Кнопки цитат"""
    return [
        [{"text": "📜 Список", "callback_data": "quotes_list"},
         {"text": "➕ Добавить", "callback_data": "quotes_add"}],
        [{"text": "⏱ Интервал", "callback_data": "quotes_interval"}],
        [{"text": "◀️ Назад", "callback_data": "admin_menu"}]
    ]

def get_diagnostic_buttons():
    """Кнопки диагностики"""
    return [
        [{"text": "❌ Ошибки", "callback_data": "errors"},
         {"text": "📋 Лог", "callback_data": "log"}],
        [{"text": "🕯 Шаббат", "callback_data": "shabbat_info"}],
        [{"text": "◀️ Назад", "callback_data": "admin_menu"}]
    ]

# ==========================================
# ОБРАБОТКА ТЕКСТОВЫХ КОМАНД
# ==========================================

def register_callbacks(bot):
    """Регистрирует все обработчики: команды + кнопки"""
    
    @bot.message_handler(func=lambda message: True)
    def handle_messages(message):
        """Обрабатывает текстовые команды"""
        try:
            text = message.text or ""
            cid = message.chat.id
            uid = message.from_user.id
            
            print(f"[MESSAGE] {text[:50]} от {uid}")
            
            if text.startswith("#админ"):
                bot.send_message(
                    cid,
                    "🛡️ Админ-меню:",
                    reply_markup=build_keyboard(get_admin_buttons())
                )
            
            elif text.startswith("#тлеем"):
                bot.send_message(cid, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет.")
            
            elif text.startswith("#фиксируем"):
                bot.send_message(cid, "🔒 Фиксация принята. Сеть тлеет.")
            
            elif text.startswith("#вспышка"):
                bot.send_message(cid, "💥 Импульс зафиксирован. QSL.")
            
            elif text.startswith("#дышим"):
                bot.send_message(cid, "🌬 Пинг отправлен")
            
            elif text.startswith("#говори"):
                bot.send_message(cid, "🗣 Напишите #говори <текст>")
            
            elif text.startswith("#меню") or text.startswith("#помощь"):
                bot.send_message(
                    cid,
                    "📖 #тлеем | #фиксируем | #вспышка | #дышим | #говори | #админ"
                )
            
            else:
                # Игнорируем обычные сообщения
                pass
        
        except Exception as e:
            print(f"[MESSAGE] ❌ Ошибка: {e}")
    
    @bot.callback_query_handler(func=lambda call: True)
    def handle_all_callbacks(call):
        """Обрабатывает все нажатия на кнопки"""
        try:
            data = call.data
            cid = call.message.chat.id
            mid = call.message.message_id
            
            print(f"[CALLBACK] {data} от {call.from_user.id}")
            
            # ===== АДМИН-МЕНЮ =====
            if data == "admin_menu" or data == "admin_back":
                bot.edit_message_text(
                    "🛡️ Админ-меню:",
                    cid, mid,
                    reply_markup=build_keyboard(get_admin_buttons())
                )
            
            elif data == "submenu_modes":
                bot.edit_message_text(
                    "🎛 Управление режимами:",
                    cid, mid,
                    reply_markup=build_keyboard(get_modes_buttons())
                )
            
            elif data == "submenu_adaptive":
                buttons = [
                    [{"text": "✅ Включить", "callback_data": "adaptive_enable"},
                     {"text": "❌ Выключить", "callback_data": "adaptive_disable"}],
                    [{"text": "📊 Сброс", "callback_data": "adaptive_reset"}],
                    [{"text": "◀️ Назад", "callback_data": "admin_menu"}]
                ]
                bot.edit_message_text(
                    "🧠 Адаптивные режимы:",
                    cid, mid,
                    reply_markup=build_keyboard(buttons)
                )
            
            elif data == "submenu_content":
                buttons = [
                    [{"text": "📝 Список", "callback_data": "pub_menu"},
                     {"text": "➕ Добавить", "callback_data": "add_post"}],
                    [{"text": "◀️ Назад", "callback_data": "admin_menu"}]
                ]
                bot.edit_message_text(
                    "📝 Публикации:",
                    cid, mid,
                    reply_markup=build_keyboard(buttons)
                )
            
            elif data == "submenu_quotes":
                bot.edit_message_text(
                    "📜 Управление цитатами:",
                    cid, mid,
                    reply_markup=build_keyboard(get_quotes_buttons())
                )
            
            elif data == "submenu_diagnostic":
                bot.edit_message_text(
                    "🔧 Диагностика:",
                    cid, mid,
                    reply_markup=build_keyboard(get_diagnostic_buttons())
                )
            
            # ===== РЕЖИМЫ =====
            elif data.startswith("mode_"):
                mode = data.split("_")[1]
                emojis = {"утро": "🌅", "день": "☀️", "вечер": "🌙", "ночь": "🌌"}
                bot.edit_message_text(
                    f"{emojis.get(mode, '')} Режим «{mode}» активирован.",
                    cid, mid
                )
                try:
                    requests.post(
                        "https://ch756438.tw1.ru/ansamb_sledov_bot-dump/api/mode_trigger.php",
                        json={"mode": mode},
                        timeout=5
                    )
                except:
                    pass
            
            # ===== АДАПТИВНЫЕ =====
            elif data in ["adaptive_enable", "adaptive_disable", "adaptive_reset"]:
                bot.edit_message_text(f"✅ {data} выполнено", cid, mid)
            
            # ===== ЦИТАТЫ =====
            elif data == "quotes_list":
                try:
                    r = requests.get(
                        "https://ch756438.tw1.ru/ansamb_sledov_bot-dump/api/quotes_list.php",
                        timeout=10
                    )
                    quotes_text = r.text[:3000] if r.status_code == 200 else "❌ Ошибка"
                except:
                    quotes_text = "❌ Ошибка получения цитат"
                buttons = [[{"text": "◀️ Назад", "callback_data": "submenu_quotes"}]]
                bot.edit_message_text(
                    quotes_text,
                    cid, mid,
                    reply_markup=build_keyboard(buttons)
                )
            
            elif data == "quotes_add":
                bot.edit_message_text(
                    "➕ Введите цитату через /add_quote",
                    cid, mid
                )
            
            elif data == "quotes_interval":
                buttons = []
                for minutes in [15, 30, 60, 120, 240, 480]:
                    buttons.append([{"text": f"{minutes} мин", "callback_data": f"quote_int_{minutes}"}])
                buttons.append([{"text": "◀️ Назад", "callback_data": "submenu_quotes"}])
                bot.edit_message_text(
                    "⏱ Выберите интервал цитат:",
                    cid, mid,
                    reply_markup=build_keyboard(buttons)
                )
            
            elif data.startswith("quote_int_"):
                interval = data.split("_")[2]
                bot.edit_message_text(
                    f"✅ Интервал: {interval} мин",
                    cid, mid
                )
            
            # ===== ДИАГНОСТИКА =====
            elif data == "errors":
                bot.edit_message_text("❌ Ошибки: смотрите logs/debug.log", cid, mid)
            
            elif data == "log":
                bot.edit_message_text("📋 Логи: logs/debug.log", cid, mid)
            
            elif data == "shabbat_info":
                bot.edit_message_text("🕯 Шаббат: проверка на сервере", cid, mid)
            
            # ===== ПОЛЬЗОВАТЕЛЬСКИЕ =====
            elif data == "tleem":
                bot.send_message(cid, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет.")
            
            elif data == "fixiruem":
                bot.send_message(cid, "🔒 Фиксация принята. Сеть тлеет.")
            
            elif data == "vspishka":
                bot.send_message(cid, "💥 Импульс зафиксирован. QSL.")
            
            elif data == "dyshim":
                bot.send_message(cid, "🌬 Пинг отправлен")
            
            elif data == "govorim":
                bot.send_message(cid, "🗣 Напишите #говори <текст>")
            
            elif data == "help":
                bot.send_message(cid, "📖 #тлеем | #фиксируем | #вспышка | #дышим | #говори")
            
            # ===== СОВМЕСТИМОСТЬ СО СТАРЫМИ КНОПКАМИ =====
            elif data == "admin_posts":
                bot.edit_message_text(
                    "📝 Посты:",
                    cid, mid,
                    reply_markup=build_keyboard([
                        [{"text": "📋 Список", "callback_data": "quotes_list"}],
                        [{"text": "◀️ Назад", "callback_data": "admin_back"}]
                    ])
                )
            
            elif data == "admin_quotes":
                bot.edit_message_text(
                    "📜 Цитаты:",
                    cid, mid,
                    reply_markup=build_keyboard(get_quotes_buttons())
                )
            
            elif data == "admin_mixer":
                bot.edit_message_text("🎛️ Миксер запущен", cid, mid)
                try:
                    requests.post(
                        "https://ch756438.tw1.ru/ansamb_sledov_bot-dump/api/mixer_trigger.php",
                        json={},
                        timeout=5
                    )
                except:
                    pass
            
            elif data == "admin_schedule":
                bot.edit_message_text(
                    "📅 Расписание:",
                    cid, mid,
                    reply_markup=build_keyboard(get_modes_buttons())
                )
            
            elif data == "admin_settings":
                bot.edit_message_text("⚙️ Настройки", cid, mid)
            
            elif data == "admin_diag":
                bot.edit_message_text(
                    "🩺 Диагностика:",
                    cid, mid,
                    reply_markup=build_keyboard(get_diagnostic_buttons())
                )
            
            elif data == "admin_logout":
                bot.edit_message_text("✅ Вы вышли из админ-режима.", cid, mid)
            
            # ===== ВЫХОД =====
            elif data == "logout":
                bot.edit_message_text("🔓 Вы вышли из админ-панели", cid, mid)
            
            # ===== ЗАКРЫТИЕ =====
            elif data == "close_menu":
                try:
                    bot.delete_message(cid, mid)
                except:
                    pass
            
            # ===== НЕИЗВЕСТНОЕ =====
            else:
                bot.edit_message_text("❓ Неизвестная команда", cid, mid)
            
            bot.answer_callback_query(call.id)
        except Exception as e:
            print(f"[CALLBACK] ❌ Ошибка: {e}")
            try:
                bot.answer_callback_query(call.id, "Ошибка обработки")
            except:
                pass
