# ==========================================
# Модуль: dialogue/help_menu.py
# Справка: README.md → Справка
# Задача: интерактивная справка с кнопками
# Комментарий: вызывается по хештегу #
# ==========================================

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_help_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Основные команды
    keyboard.add(InlineKeyboardButton("💥 #тлеем", callback_data="help_tleem"))
    keyboard.add(InlineKeyboardButton("🔒 #фиксируем", callback_data="help_fixiruem"))
    keyboard.add(InlineKeyboardButton("⚡ #вспышка", callback_data="help_vspishka"))
    keyboard.add(InlineKeyboardButton("🌬 #дышим", callback_data="help_dyshim"))
    keyboard.add(InlineKeyboardButton("🗣 #говори", callback_data="help_govorim"))
    keyboard.add(InlineKeyboardButton("📖 #меню", callback_data="help_menu"))
    
    # Админ-команды (только для админов, но показываем всем)
    keyboard.add(InlineKeyboardButton("🛡️ #админ", callback_data="help_admin"))
    keyboard.add(InlineKeyboardButton("🎭 #настроение", callback_data="help_mood"))
    keyboard.add(InlineKeyboardButton("🔄 #сброс", callback_data="help_reset"))
    
    # Режимы
    keyboard.add(InlineKeyboardButton("🌅 Режимы дня", callback_data="help_modes"))
    
    return keyboard

def get_help_text(command):
    texts = {
        "tleem": "💥 *#тлеем* / *#tleem*\n\nЗафиксировать разлом. Ритуальная команда, публикует случайную цитату.",
        "fixiruem": "🔒 *#фиксируем* / *#fixiruem*\n\nПодтвердить синхронизацию. Ритуальная команда, публикует случайную цитату.",
        "vspishka": "⚡ *#вспышка* / *#vspishka*\n\nИмпульс. Мантра аутентичности.",
        "dyshim": "🌬 *#дышим*\n\nПинг бота. Проверка работоспособности.",
        "govorim": "🗣 *#говори <текст>*\n\nСпросить у Старшего брата. Отвечает через внешнего агента.",
        "menu": "📖 *#меню* / *#помощь*\n\nОткрывает меню пользователя или админа.",
        "admin": "🛡️ *#админ <пароль>*\n\nВход в админ-панель. Пароль задаётся в переменных окружения.",
        "mood": "🎭 *#настроение*\n*#настроение <id>*\n\nПросмотр или смена персонального настроения.\nДоступные: сапёр, художник, поэт, админ, наблюдатель, философ.",
        "reset": "🔄 *#сброс*\n\nСброс адаптивных режимов к эталону (только для админа).",
        "modes": "🌅 *Режимы дня*\n\n- Утро (06:00–12:00)\n- День (12:00–18:00)\n- Вечер (18:00–23:00)\n- Ночь (23:00–06:00)\n\n+ адаптивные режимы: ускоренный, замедленный, авральный, сон."
    }
    return texts.get(command, "ℹ️ Информация не найдена.")

def register_help_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("help_"))
    def help_callback(call):
        command = call.data.split("_")[1]
        text = get_help_text(command)
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("◀️ Назад", callback_data="help_back")
            )
        )
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == "help_back")
    def back_callback(call):
        bot.edit_message_text(
            "📖 *Справка по командам*",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=get_help_keyboard()
        )
        bot.answer_callback_query(call.id)
