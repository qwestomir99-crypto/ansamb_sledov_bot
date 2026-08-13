# ==========================================
# Файл: render_callbacks.py (для Render)
# Справка: README.md → Telegram прокси / Render / Кнопки
# Задача: обработчики текстовых команд и callback'ов на Render
# Комментарий: вызывается из bot.py на Render. Подробное логирование.
# Зависит от: telebot, requests
# Вызывается из: bot.py (Render)
# Версия: 2.1 — добавлено подробное логирование для отладки
# ==========================================

import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

print("[CALLBACKS] render_callbacks.py загружен")

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

def build_keyboard(buttons_data):
    """Строит клавиатуру из JSON-списка"""
    try:
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
    except Exception as e:
        print(f"[CALLBACKS] ❌ Ошибка build_keyboard: {e}")
        return None

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
# РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ
# ==========================================

def register_callbacks(bot):
    """Регистрирует все обработчики: команды + кнопки"""
    print("[CALLBACKS] Регистрация обработчиков...")
    
    @bot.message_handler(func=lambda message: True)
    def handle_messages(message):
        """Обрабатывает текстовые команды"""
        try:
            text = message.text or ""
            cid = message.chat.id
            uid = message.from_user.id
            
            print(f"[MESSAGE] Получено: '{text[:50]}' от user_id={uid}")
            
            if text.startswith("#админ"):
                print(f"[MESSAGE] Команда #админ от {uid}")
                bot.send_message(
                    cid,
                    "🛡️ Админ-меню:",
                    reply_markup=build_keyboard(get_admin_buttons())
                )
                print(f"[MESSAGE] Кнопки админа отправлены")
            
            elif text.startswith("#тлеем"):
                print(f"[MESSAGE] Команда #тлеем от {uid}")
                bot.send_message(cid, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет.")
            
            elif text.startswith("#фиксируем"):
                print(f"[MESSAGE] Команда #фиксируем от {uid}")
                bot.send_message(cid, "🔒 Фиксация принята. Сеть тлеет.")
            
            elif text.startswith("#вспышка"):
                print(f"[MESSAGE] Команда #вспышка от {uid}")
                bot.send_message(cid, "💥 Импульс зафиксирован. QSL.")
            
            elif text.startswith("#дышим"):
                print(f"[MESSAGE] Команда #дышим от {uid}")
                bot.send_message(cid, "🌬 Пинг отправлен")
            
            elif text.startswith("#говори"):
                print(f"[MESSAGE] Команда #говори от {uid}")
                bot.send_message(cid, "🗣 Напишите #говори <текст>")
            
            elif text.startswith("#меню") or text.startswith("#помощь"):
                print(f"[MESSAGE] Команда #меню от {uid}")
                bot.send_message(
                    cid,
                    "📖 #тлеем | #фиксируем | #вспышка | #дышим | #говори | #админ"
                )
            
            else:
                print(f"[MESSAGE] Проигнорировано: '{text[:30]}'")
        
        except Exception as e:
            print(f"[MESSAGE] ❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    @bot.callback_query_handler(func=lambda call: True)
    def handle_all_callbacks(call):
        """Обрабатывает все нажатия на кнопки"""
        try:
            data = call.data
            cid = call.message.chat.id
            mid = call.message.message_id
            
            print(f"[CALLBACK] Получен: '{data}' от user_id={call.from_user.id}")
            
            # ===== АДМИН-МЕНЮ =====
            if data == "admin_menu" or data == "admin_back":
                print("[CALLBACK] → Показ админ-меню")
                bot.edit_message_text(
                    "🛡️ Админ-меню:",
                    cid, mid,
                    reply_markup=build_keyboard(get_admin_buttons())
                )
            
            elif data == "submenu_modes":
                print("[CALLBACK] → Подменю режимов")
                bot.edit_message_text(
                    "🎛 Управление режимами:",
                    cid, mid,
                    reply_markup=build_keyboard(get_modes_buttons())
                )
            
            elif data == "submenu_adaptive":
                print("[CALLBACK] → Подменю адаптивных")
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
                print("[CALLBACK] → Подменю контента")
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
                print("[CALLBACK] → Подменю цитат")
                bot.edit_message_text(
                    "📜 Управление цитатами:",
                    cid, mid,
                    reply_markup=build_keyboard(get_quotes_buttons())
                )
            
            elif data == "submenu_diagnostic":
                print("[CALLBACK] → Подменю диагностики")
                bot.edit_message_text(
                    "🔧 Диагностика:",
                    cid, mid,
                    reply_markup=build_keyboard(get_diagnostic_buttons())
                )
            
            # ===== СОВМЕСТИМОСТЬ СО СТАРЫМИ КНОПКАМИ =====
            elif data == "admin_posts":
                print("[CALLBACK] → Старая кнопка admin_posts")
                bot.edit_message_text("📝 Посты", cid, mid)
            
            elif data == "admin_quotes":
                print("[CALLBACK] → Старая кнопка admin_quotes")
                bot.edit_message_text(
                    "📜 Цитаты:",
                    cid, mid,
                    reply_markup=build_keyboard(get_quotes_buttons())
                )
            
            elif data == "admin_mixer":
                print("[CALLBACK] → Миксер")
                bot.edit_message_text("🎛️ Миксер запущен", cid, mid)
            
            elif data == "admin_schedule":
                print("[CALLBACK] → Расписание")
                bot.edit_message_text(
                    "📅 Расписание:",
                    cid, mid,
                    reply_markup=build_keyboard(get_modes_buttons())
                )
            
            elif data == "admin_settings":
                print("[CALLBACK] → Настройки")
                bot.edit_message_text("⚙️ Настройки", cid, mid)
            
            elif data == "admin_diag":
                print("[CALLBACK] → Диагностика (старая)")
                bot.edit_message_text(
                    "🩺 Диагностика:",
                    cid, mid,
                    reply_markup=build_keyboard(get_diagnostic_buttons())
                )
            
            elif data == "admin_logout":
                print("[CALLBACK] → Выход из админки")
                bot.edit_message_text("✅ Вы вышли из админ-режима.", cid, mid)
            
            # ===== ПОЛЬЗОВАТЕЛЬСКИЕ =====
            elif data == "tleem":
                print("[CALLBACK] → #тлеем")
                bot.send_message(cid, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет.")
            
            elif data == "fixiruem":
                print("[CALLBACK] → #фиксируем")
                bot.send_message(cid, "🔒 Фиксация принята. Сеть тлеет.")
            
            elif data == "vspishka":
                print("[CALLBACK] → #вспышка")
                bot.send_message(cid, "💥 Импульс зафиксирован. QSL.")
            
            elif data == "dyshim":
                print("[CALLBACK] → #дышим")
                bot.send_message(cid, "🌬 Пинг отправлен")
            
            elif data == "govorim":
                print("[CALLBACK] → #говори")
                bot.send_message(cid, "🗣 Напишите #говори <текст>")
            
            elif data == "help":
                print("[CALLBACK] → Справка")
                bot.send_message(cid, "📖 #тлеем | #фиксируем | #вспышка | #дышим | #говори")
            
            # ===== ВЫХОД / ЗАКРЫТИЕ =====
            elif data == "logout":
                print("[CALLBACK] → Выход")
                bot.edit_message_text("🔓 Вы вышли из админ-панели", cid, mid)
            
            elif data == "close_menu":
                print("[CALLBACK] → Закрытие меню")
                try:
                    bot.delete_message(cid, mid)
                except:
                    pass
            
            # ===== НЕИЗВЕСТНОЕ =====
            else:
                print(f"[CALLBACK] ❓ Неизвестная команда: {data}")
                bot.edit_message_text("❓ Неизвестная команда", cid, mid)
            
            bot.answer_callback_query(call.id)
            print(f"[CALLBACK] Обработан: {data}")
        except Exception as e:
            print(f"[CALLBACK] ❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            try:
                bot.answer_callback_query(call.id, "Ошибка обработки")
            except:
                pass
    
    print("[CALLBACKS] ✅ Обработчики зарегистрированы")
