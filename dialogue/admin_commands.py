# ==========================================
# Файл: dialogue/admin_commands.py
# Справка: README.md → Админ-панель
# Задача: команда #админ, авторизация, вызов меню, ПРЯМАЯ ПУБЛИКАЦИЯ ПОСТОВ
# ==========================================

import os
import threading
import time
from debug_utils import debug_log
from dialogue.button_map import get_admin_menu_keyboard

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "tleem2026")

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
    
    bot.reply_to(message, "🔐 Введите пароль для входа в админ-панель:\n(или #админ пароль)")

# ==========================================
# ПРЯМАЯ ПУБЛИКАЦИЯ ПОСТА (без сохранения в пул)
# ==========================================

def show_add_post_ui(call, bot):
    # Удаляем старое меню
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    # Отправляем новое сообщение
    msg = bot.send_message(
        call.message.chat.id,
        "📝 *Публикация поста*\n\n"
        "Пришлите текст поста (можно с фото/видео).\n"
        "Для отмены введите /cancel",
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)
    bot.register_next_step_handler(msg, publish_post, bot)

def publish_post(message, bot):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Публикация отменена.")
        return
    
    # Получаем текст и теги
    text = message.caption if message.photo else message.text
    if not text:
        bot.reply_to(message, "❌ Добавьте текст к посту.")
        return
    
    tags = [word for word in text.split() if word.startswith('#')]
    tags_str = " ".join(tags)
    
    # Получаем file_id (если есть фото/видео)
    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id
    
    # === ПУБЛИКАЦИЯ ===
    config = load_config()
    tg_chat_id = config.get("telegram", {}).get("publish_channel", "@qwestomir")
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    from dialogue.publisher_utils import post_to_telegram, post_to_vk
    
    success_tg = False
    success_vk = False
    
    # Публикуем в Telegram
    if tg_chat_id:
        success_tg = post_to_telegram(bot, tg_chat_id, text, file_id, tags_str)
        debug_log("PUBLISH", f"Telegram: {'✅' if success_tg else '❌'}")
    
    # Публикуем в VK
    if vk_token and vk_owner_id:
        success_vk, _ = post_to_vk(text, tags_str, vk_token, vk_owner_id, file_id)
        debug_log("PUBLISH", f"VK: {'✅' if success_vk else '❌'}")
    
    if success_tg or success_vk:
        bot.reply_to(message, "✅ *Пост опубликован!*", parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ *Ошибка при публикации.*", parse_mode='Markdown')

def load_config():
    import json
    with open("config.json", "r") as f:
        return json.load(f)
