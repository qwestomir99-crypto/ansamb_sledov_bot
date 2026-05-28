# ==========================================
# Файл: bot/handlers/menu.py
# Справка: README.md → Обработчики команд / Меню
# Задача: команды #меню, #помощь
# ==========================================

def register_menu_handler(bot, config):
    @bot.message_handler(func=lambda message: message.text.lower() in ["#меню", "#помощь"])
    def handle_menu(message):
        from dialogue.admin_commands import is_admin_authorized, get_admin_menu, get_user_menu
        if is_admin_authorized(message.from_user.id):
            bot.reply_to(message, "🛡️ Админ-меню:", reply_markup=get_admin_menu())
        else:
            bot.reply_to(message, "📋 Ваше меню:", reply_markup=get_user_menu())
