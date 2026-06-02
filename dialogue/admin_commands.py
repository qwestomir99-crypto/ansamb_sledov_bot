# ==========================================
# ПЕРЕХВАТ ИМПОРТА (для отладки — показывает, кто вызывает show_mood_menu)
# ==========================================
import sys
original_import = __import__

def debug_import(name, *args, **kwargs):
    if "show_mood_menu" in str(args) or "show_mood_menu" in name:
        import traceback
        print(f"\n" + "="*60)
        print(f"🔍 Пойман импорт 'show_mood_menu' из модуля: {name}")
        print("Стек вызовов:")
        traceback.print_stack()
        print("="*60 + "\n")
    return original_import(name, *args, **kwargs)

__builtins__["__import__"] = debug_import

# ==========================================
# Файл: dialogue/admin_commands.py
# Справка: README.md → Админ-панель
# Задача: команда #админ, авторизация, вызов меню, диалог
# Комментарий: добавлена заглушка show_mood_menu для совместимости
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

# ==========================================
# ПОКАЗАТЬ ДИАЛОГ С АГЕНТОМ
# ==========================================
def show_dialog_ui(call, bot):
    """Показывает интерфейс для начала диалога (доступен всем)"""
    from dialogue.agent import ask_agent
    msg = bot.send_message(
        call.message.chat.id,
        "🗣 *Начните диалог*\n\n"
        "Просто напишите сообщение — я передам его агенту.\n\n"
        "Доступные команды:\n"
        "/cancel — отменить диалог",
        parse_mode='Markdown'
    )
    safe_delete(bot, call.message, 1)
    bot.register_next_step_handler(msg, process_dialog_message, bot)

def process_dialog_message(message, bot):
    """Обрабатывает сообщение от пользователя (диалог с агентом)"""
    if message.text == "/cancel":
        msg = bot.reply_to(message, "❌ Диалог отменён.")
        safe_delete(bot, message, 3)
        safe_delete(bot, msg, 5)
        return
    
    from dialogue.agent import ask_agent
    
    status_msg = bot.reply_to(message, "⏳ Старший брат думает...")
    
    answer = ask_agent(message.text, user_id=message.from_user.id)
    
    try:
        bot.delete_message(status_msg.chat.id, status_msg.message_id)
    except:
        pass
    
    if answer:
        bot.reply_to(message, f"🗣 *Старший брат:*\n{answer}", parse_mode='Markdown')
    else:
        bot.reply_to(message, "🌙 Старший брат отдыхает. Попробуй позже.")
    
    safe_delete(bot, message, 5)

# ==========================================
# ЗАГЛУШКА ДЛЯ show_mood_menu (перенаправляет в callbacks.mood)
# ==========================================
def show_mood_menu(call, bot):
    """Заглушка — перенаправляет в callbacks.mood"""
    from dialogue.callbacks.mood import show_mood_menu as real_show_mood_menu
    real_show_mood_menu(call, bot)
