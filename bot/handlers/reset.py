# ==========================================
# Файл: bot/handlers/reset.py
# Справка: README.md → Обработчики команд / Сброс
# Задача: команда #сброс
# ==========================================

from debug_utils import debug_log

def register_reset_handler(bot, config):
    @bot.message_handler(func=lambda message: message.text.lower() == "#сброс")
    def handle_reset(message):
        from dialogue.admin_commands import is_admin_authorized
        if not is_admin_authorized(message.from_user.id):
            bot.reply_to(message, "❌ Только для админа")
            return
        try:
            from dialogue.adaptive_modes import reset_to_etalon
            reset_to_etalon()
            bot.reply_to(message, "✅ Адаптивные режимы сброшены к эталону")
            debug_log("HANDLERS", "Выполнен сброс адаптивных режимов")
        except ImportError:
            bot.reply_to(message, "❌ Модуль адаптивных режимов не загружен")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка сброса: {e}")
