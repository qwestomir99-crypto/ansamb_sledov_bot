# ==========================================
# Файл: dialogue/admin_commands.py
# Справка: README.md → Админ-панель
# Задача: команда #админ, авторизация, вызов меню, диалог
# Комментарий: добавлен пошаговый ввод поста (без register_next_step_handler)
# ==========================================

import os
import threading
import time
from debug_utils import debug_log
from dialogue.button_map import get_admin_menu_keyboard
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "tleem2026")

authorized_admins = {}

# Временное хранилище для черновиков постов
post_drafts = {}

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

def safe_delete(bot, message, delay=3):
    def _delete():
        time.sleep(delay)
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
    threading.Thread(target=_delete, daemon=True).start()

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
# ПОШАГОВОЕ ДОБАВЛЕНИЕ ПОСТА (без register_next_step_handler)
# ==========================================

def show_add_post_ui(call, bot):
    """Показывает интерфейс добавления поста (шаг 1: текст)"""
    user_id = call.from_user.id
    post_drafts[user_id] = {}
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel_add_post"))
    
    bot.edit_message_text(
        "📝 *Шаг 1 из 2: текст поста*\n\n"
        "Напишите текст поста (можно с Markdown).\n"
        "После отправки текста нажмите кнопку 'Готово'.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    bot.answer_callback_query(call.id)

def process_post_text_message(message, bot):
    """Обрабатывает текст поста, отправленный пользователем"""
    user_id = message.from_user.id
    if user_id not in post_drafts:
        return
    
    post_drafts[user_id]["text"] = message.text
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Готово", callback_data="finish_post"),
        InlineKeyboardButton("✏️ Заново", callback_data="restart_post"),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel_add_post")
    )
    
    bot.reply_to(
        message,
        f"📝 *Текст сохранён:*\n\n{message.text[:200]}{'...' if len(message.text) > 200 else ''}\n\n"
        f"Теперь нажмите 'Готово' для ввода тегов.",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    safe_delete(bot, message, 2)

def show_tags_ui(call, bot):
    """Показывает интерфейс ввода тегов (шаг 2)"""
    user_id = call.from_user.id
    if user_id not in post_drafts or "text" not in post_drafts[user_id]:
        bot.answer_callback_query(call.id, "❌ Ошибка: текст не найден")
        return
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("⏭️ Пропустить теги", callback_data="skip_tags"),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel_add_post")
    )
    
    bot.edit_message_text(
        "🏷️ *Шаг 2 из 2: теги*\n\n"
        "Введите теги через пробел (например: #тлеем #ансамбль).\n"
        "Или нажмите 'Пропустить теги'.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    bot.answer_callback_query(call.id)

def process_tags_message(message, bot):
    """Обрабатывает теги, отправленные пользователем"""
    user_id = message.from_user.id
    if user_id not in post_drafts or "text" not in post_drafts[user_id]:
        return
    
    tags = message.text.split()
    post_drafts[user_id]["tags"] = tags
    
    # Сохраняем пост
    from dialogue.post_manager import add_post_to_pool
    text = post_drafts[user_id]["text"]
    success = add_post_to_pool(text, tags, author_id=user_id)
    
    if success:
        bot.reply_to(message, "✅ *Пост добавлен в пул публикаций!*", parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ *Ошибка при сохранении поста.*", parse_mode='Markdown')
    
    # Чистим черновик
    del post_drafts[user_id]
    safe_delete(bot, message, 2)

def finish_post_without_tags(call, bot):
    """Завершает добавление поста без тегов"""
    user_id = call.from_user.id
    if user_id not in post_drafts or "text" not in post_drafts[user_id]:
        bot.answer_callback_query(call.id, "❌ Ошибка: текст не найден")
        return
    
    from dialogue.post_manager import add_post_to_pool
    text = post_drafts[user_id]["text"]
    success = add_post_to_pool(text, [], author_id=user_id)
    
    if success:
        bot.edit_message_text(
            "✅ *Пост добавлен в пул публикаций!*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown'
        )
    else:
        bot.edit_message_text(
            "❌ *Ошибка при сохранении поста.*",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown'
        )
    
    del post_drafts[user_id]
    bot.answer_callback_query(call.id)

def cancel_add_post(call, bot):
    """Отменяет добавление поста"""
    user_id = call.from_user.id
    if user_id in post_drafts:
        del post_drafts[user_id]
    bot.edit_message_text(
        "❌ *Добавление поста отменено.*",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

# ==========================================
# ДИАЛОГ С АГЕНТОМ
# ==========================================

def show_dialog_ui(call, bot):
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
