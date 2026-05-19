# ==========================================
# Модуль: dialogue/help_menu.py
# Справка: README.md → Справка
# Задача: интерактивная справка с кнопками
# Комментарий: вызывается по хештегу #
# Зависит от: telebot
# Вызывается из: handlers.py, callbacks.py
# ==========================================

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_help_keyboard():
    """Возвращает клавиатуру с командами"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Основные команды
    keyboard.add(
        InlineKeyboardButton("💥 #тлеем", callback_data="help_tleem"),
        InlineKeyboardButton("🔒 #фиксируем", callback_data="help_fixiruem")
    )
    keyboard.add(
        InlineKeyboardButton("⚡ #вспышка", callback_data="help_vspishka"),
        InlineKeyboardButton("🌬 #дышим", callback_data="help_dyshim")
    )
    keyboard.add(
        InlineKeyboardButton("🗣 #говори", callback_data="help_govorim"),
        InlineKeyboardButton("📖 #меню", callback_data="help_menu_cmd")
    )
    
    # Админ-команды
    keyboard.add(
        InlineKeyboardButton("🛡️ #админ", callback_data="help_admin"),
        InlineKeyboardButton("🎭 #настроение", callback_data="help_mood")
    )
    keyboard.add(
        InlineKeyboardButton("🔄 #сброс", callback_data="help_reset"),
        InlineKeyboardButton("🌅 Режимы дня", callback_data="help_modes")
    )
    
    return keyboard

def get_help_text(command):
    """Возвращает описание команды"""
    texts = {
        "tleem": "💥 *#тлеем* / *#tleem*\n\nЗафиксировать разлом. Ритуальная команда, публикует случайную цитату.\n\nПример: `#тлеем`",
        "fixiruem": "🔒 *#фиксируем* / *#fixiruem*\n\nПодтвердить синхронизацию. Ритуальная команда, публикует случайную цитату.\n\nПример: `#фиксируем`",
        "vspishka": "⚡ *#вспышка* / *#vspishka*\n\nИмпульс. Мантра аутентичности.\n\nПример: `#вспышка`",
        "dyshim": "🌬 *#дышим*\n\nПинг бота. Проверка работоспособности.\n\nПример: `#дышим`",
        "govorim": "🗣 *#говори <текст>*\n\nСпросить у Старшего брата. Отвечает через внешнего агента.\n\nПример: `#говори Как ритм?`",
        "menu_cmd": "📖 *#меню* / *#помощь*\n\nОткрывает меню пользователя или админа (после авторизации).\n\nПример: `#меню`",
        "admin": "🛡️ *#админ <пароль>*\n\nВход в админ-панель. Пароль задаётся в переменных окружения Render.\n\nПример: `#админ ne_tleem2026`",
        "mood": "🎭 *#настроение*\n*#настроение <id>*\n\nПросмотр или смена персонального настроения.\n\nДоступные настроения:\n• `сапёр` — факты, логи\n• `художник` — образы, метафоры\n• `поэт` — тишина, рифмы\n• `админ` — команды, сводки\n• `наблюдатель` — тихое наблюдение\n• `философ` — глубокие вопросы\n\nПример: `#настроение художник`",
        "reset": "🔄 *#сброс*\n\nСброс адаптивных режимов к эталону. Только для админа.\n\nПример: `#сброс`",
        "modes": "🌅 *Режимы дня*\n\n⏰ *Утро* (06:00–12:00)\n☀️ *День* (12:00–18:00)\n🌙 *Вечер* (18:00–23:00)\n😴 *Ночь* (23:00–06:00)\n\n⚡ *Адаптивные режимы:*\n• ускоренный — высокая активность\n• замедленный — мало активности\n• авральный — много ошибок\n• сон — полное затишье\n\nРитм 0,8 Гц стабилен."
    }
    return texts.get(command, "ℹ️ *Команда не найдена*\n\nПопробуйте `#справка` для полного списка.")

def register_help_handlers(bot):
    """Регистрирует обработчики кнопок справки"""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("help_"))
    def help_callback(call):
        command = call.data.split("_")[1]
        text = get_help_text(command)
        
        # Создаём клавиатуру с кнопкой "Назад"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("◀️ Назад к списку", callback_data="help_back"))
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "help_back")
    def back_callback(call):
        bot.edit_message_text(
            "📖 *Справка по командам*\n\nВыберите команду для подробного описания:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=get_help_keyboard()
        )
        bot.answer_callback_query(call.id)
