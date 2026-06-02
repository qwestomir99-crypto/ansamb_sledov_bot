# ==========================================
# Файл: dialogue/admin_commands.py
# Справка: README.md → Админ-панель
# Задача: команда #админ, авторизация, вызов меню
# Комментарий: без обработки кнопок и диалогов
# Зависит от: telebot, button_map, debug_utils
# Вызывается из: bot/handlers/__init__.py
# ==========================================

import os
import threading
import time
from debug_utils import debug_log
from dialogue.button_map import get_admin_menu_keyboard

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "tleem2026")

# ==========================================
# АВТОРИЗАЦИЯ
# ==========================================
authorized_admins = {}

def is_admin_authorized(user_id):
    return authorized_admins.get(user_id, False)

def authorize_admin(user_id, password):
    if password == ADMIN_PASSWORD:
        authorized_admins[user_id] = True
        debug_log("ADMIN", f"Админ {user_id} авторизован")
        return True
    return False

def logout_admin(user_id):
    if user_id in authorized_admins:
        del authorized_admins[user_id]
        debug_log("ADMIN", f"Админ {user_id} вышел")

# ==========================================
# БЕЗОПАСНОЕ УДАЛЕНИЕ СООБЩЕНИЙ
# ==========================================
def safe_delete(bot, message, delay=3):
    def _delete():
        time.sleep(delay)
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
    threading.Thread(target=_delete, daemon=True).start()

# ==========================================
# ОБРАБОТЧИК КОМАНДЫ #админ
# ==========================================
def handle_admin_command(message, bot):
    user_id = message.from_user.id
    text = message.text.lower()
    
    if is_admin_authorized(user_id):
        bot.reply_to(message, "🛡️ Админ-меню:", reply_markup=get_admin_menu_keyboard())
        safe_delete(bot, message, 3)
        return
    
    parts = text.split(maxsplit=1)
    if len(parts) > 1:
        password = parts[1]
        if authorize_admin(user_id, password):
            bot.reply_to(message, "✅ Авторизация успешна!", reply_markup=get_admin_menu_keyboard())
            safe_delete(bot, message, 3)
        else:
            msg = bot.reply_to(message, "❌ Неверный пароль.")
            safe_delete(bot, message, 3)
            safe_delete(bot, msg, 5)
        return
    
    bot.reply_to(message, f"🔐 Введите пароль:\n`#админ {ADMIN_PASSWORD}`", parse_mode='Markdown')
