# ==========================================
# Модуль: dialogue/help_menu.py
# Справка: README.md → Справка
# Задача: интерактивная справка с кнопками
# Комментарий: вызывается по хештегу #
# ==========================================

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_help_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    
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
    keyboard.add(
        InlineKeyboardButton("🛡️ #админ", callback_data="help_admin"),
        InlineKeyboardButton("🎭 #настроение", callback_data="help_mood")
    )
    keyboard.add(
        InlineKeyboardButton("🔄 #сброс", callback_data="help_reset"),
        InlineKeyboardButton("🌅 Режимы дня", callback_data="help_modes")
    )
    keyboard.add(InlineKeyboardButton("❌ Выход", callback_data="help_exit"))
    
    return keyboard

def get_help_text(command):
    texts = {
        "tleem": "💥 *#тлеем* / *#tleem*\n\nЗафиксировать разлом. Ритуальная команда, публикует случайную цитату.\n\nПример: `#тлеем`",
        "fixiruem": "🔒 *#фиксируем* / *#fixiruem*\n\nПодтвердить синхронизацию. Ритуальная команда, публикует случайную цитату.\n\nПример: `#фиксируем`",
        "vspishka": "⚡ *#вспышка* / *#vspishka*\n\nИмпульс. Мантра аутентичности.\n\nПример: `#вспышка`",
        "dyshim": "🌬 *#дышим*\n\nПинг бота. Проверка работоспособности.\n\nПример: `#дышим`",
        "govorim": "🗣 *#говори <текст>*\n\nСпросить у Старшего брата. Отвечает через внешнего агента.\n\nПример: `#говори Как ритм?`",
        "menu_cmd": "📖 *#меню* / *#помощь*\n\nОткрывает меню пользователя или админа (после авторизации).\n\nПример: `#меню`",
        "admin": "🛡️ *#админ <пароль>*\n\nВход в админ-панель. Пароль задаётся в переменных окружения Render.\n\nПример: `#админ ne_tleem2026`",
        "mood": "🎭 *#настроение*\n\nОткрывает меню выбора персонального настроения.\n\nПример: `#настроение`",
        "reset": "🔄 *#сброс*\n\nСброс адаптивных режимов к эталону. Только для админа.\n\nПример: `#сброс`",
        "modes": "🌅 *Режимы дня*\n\n⏰ *Утро* (06:00–12:00)\n☀️ *День* (12:00–18:00)\n🌙 *Вечер* (18:00–23:00)\n😴 *Ночь* (23:00–06:00)\n\n⚡ *Адаптивные режимы:*\n• ускоренный — высокая активность\n• замедленный — мало активности\n• авральный — много ошибок\n• сон — полное затишье\n\nРитм 0,8 Гц стабилен."
    }
    return texts.get(command, "ℹ️ *Команда не найдена*\n\nПопробуйте `#` для интерактивной справки.")

def register_help_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("help_"))
    def help_callback(call):
        command = call.data.split("_")[1]
        
        # Кнопка выхода
        if command == "exit":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(call.id, "Справка закрыта")
            return
        
        text = get_help_text(command)
        
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("◀️ Назад к списку", callback_data="help_back"),
            InlineKeyboardButton("❌ Выход", callback_data="help_exit")
        )
        
        try:
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        except Exception as e:
            if "message is not modified" not in str(e):
                print(f"[HELP_MENU] Ошибка: {e}")
        
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
