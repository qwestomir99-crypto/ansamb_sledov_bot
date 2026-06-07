# ==========================================
# Файл: dialogue/admin/posts.py
# Справка: README.md → Админка (публикации)
# Задача: TG-посты, отложенные публикации, интервал, VK
# Комментарий: VK — группа через VK_GROUP_ID
# ==========================================

import os, json, tempfile
from dialogue.post_manager import add_post_to_pool, load_post_pool
from dialogue.publisher_utils import get_auto_tags, get_random_quote, post_to_vk
from debug_utils import debug_log

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f: return json.load(f)

def show_add_post_ui(call, bot):
    from dialogue.admin_commands import safe_delete
    msg = bot.send_message(call.message.chat.id, "📝 *Добавление поста*\n\nПришлите текст.\nИли /cancel.", parse_mode='Markdown')
    safe_delete(call.message, 1)
    bot.register_next_step_handler(msg, process_post_text, bot)

def process_post_text(message, bot):
    from dialogue.admin_commands import safe_delete, get_admin_menu
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Отменено.", reply_markup=get_admin_menu()); safe_delete(message, 3); return
    if not hasattr(process_post_text, "temp_posts"): process_post_text.temp_posts = {}
    process_post_text.temp_posts[message.from_user.id] = {"text": message.text}
    msg = bot.send_message(message.chat.id, "🏷️ Теги через пробел или /skip")
    bot.register_next_step_handler(msg, process_post_tags, bot, message.from_user.id)
    safe_delete(message, 2)

def process_post_tags(message, bot, user_id):
    from dialogue.admin_commands import safe_delete, get_admin_menu
    if message.text == "/skip": tags = []
    elif message.text == "/cancel":
        bot.reply_to(message, "❌ Отменено.", reply_markup=get_admin_menu()); safe_delete(message, 3); return
    else: tags = message.text.split()
    post_data = getattr(process_post_text, "temp_posts", {}).get(user_id, {})
    text = post_data.get("text", "")
    if not hasattr(process_post_tags, "pending_posts"): process_post_tags.pending_posts = {}
    process_post_tags.pending_posts[user_id] = {"text": text, "tags": tags}
    msg = bot.send_message(message.chat.id, "📋 *Пост готов.*\n`0` — сейчас, или число минут.\n/cancel — отмена", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_publish_choice, bot, user_id)
    safe_delete(message, 3)

def process_publish_choice(message, bot, user_id):
    from dialogue.admin_commands import safe_delete, get_admin_menu
    choice = message.text.strip().lower()
    if choice == "/cancel":
        bot.reply_to(message, "❌ Отменена.", reply_markup=get_admin_menu()); safe_delete(message, 3); return
    post_data = getattr(process_post_tags, "pending_posts", {}).get(user_id, {})
    text, tags = post_data.get("text", ""), post_data.get("tags", [])
    try: delay = int(choice)
    except:
        bot.reply_to(message, "❌ Введите число (0 = сейчас).", reply_markup=get_admin_menu()); safe_delete(message, 5); return
    from dialogue.publisher import publish_now_or_later
    success = publish_now_or_later(bot, user_id, text, tags, delay)
    bot.reply_to(message, "✅ Опубликовано!" if (success and delay == 0) else ("✅ В пул!" if success else "❌ Ошибка."), reply_markup=get_admin_menu())
    safe_delete(message, 5)

def set_publish_interval_ui(call, bot):
    from dialogue.admin_commands import safe_delete, get_admin_menu
    config = load_config()
    current = config.get("publisher", {}).get("interval_minutes", 120)
    msg = bot.send_message(call.message.chat.id, f"⏱️ *Интервал постов*\nТекущий: {current} мин.\nВведите от 10 до 1440.\n/cancel.", parse_mode='Markdown')
    safe_delete(call.message, 1)
    bot.register_next_step_handler(msg, process_publish_interval, bot)

def process_publish_interval(message, bot):
    from dialogue.admin_commands import safe_delete, get_admin_menu
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Отменено.", reply_markup=get_admin_menu()); safe_delete(message, 3); return
    try:
        interval = int(message.text.strip())
        if 10 <= interval <= 1440:
            config = load_config()
            if "publisher" not in config: config["publisher"] = {}
            config["publisher"]["interval_minutes"] = interval
            config["publisher"]["interval_seconds"] = interval * 60
            with open(CONFIG_FILE, "w") as f: json.dump(config, f, indent=2)
            bot.reply_to(message, f"✅ Интервал постов: {interval} мин.", reply_markup=get_admin_menu())
        else: raise ValueError
    except: bot.reply_to(message, "❌ Число от 10 до 1440.", reply_markup=get_admin_menu())
    safe_delete(message, 5)

def handle_vk_post(bot, chat_id, message_id, user_id):
    msg = bot.send_message(chat_id, "✍️ Введите текст поста для VK:")
    bot.register_next_step_handler(msg, process_vk_post_text, bot, chat_id, user_id)

def process_vk_post_text(message, bot, chat_id, user_id):
    text = message.text.strip()
    if not text: bot.send_message(chat_id, "❌ Текст не может быть пустым"); return
    msg = bot.send_message(chat_id, "📎 Пришлите фото, видео или /skip")
    bot.register_next_step_handler(msg, process_vk_post_file, bot, chat_id, text, user_id)

def process_vk_post_file(message, bot, chat_id, text, user_id):
    file_path = None
    if message.text and message.text.lower() == "/skip": file_path = None
    elif message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_path = os.path.join(tempfile.gettempdir(), f"temp_vk_{message.photo[-1].file_id}.jpg")
        with open(file_path, 'wb') as f: f.write(bot.download_file(file_info.file_path))
    elif message.video:
        file_info = bot.get_file(message.video.file_id)
        file_path = os.path.join(tempfile.gettempdir(), f"temp_vk_{message.video.file_id}.mp4")
        with open(file_path, 'wb') as f: f.write(bot.download_file(file_info.file_path))
    
    vk_token = os.environ.get("VK_TOKEN")
    vk_group_id = os.environ.get("VK_GROUP_ID")
    if not vk_token or not vk_group_id:
        bot.send_message(chat_id, "❌ VK отключён."); return
    
    full_text = f"{text}\n\n📜 {get_random_quote()}"
    auto_tags = get_auto_tags(text, "vk")
    success, error_msg = post_to_vk(full_text, auto_tags, vk_token, vk_group_id, file_path, auto_quote=False, auto_tags=False)
    bot.send_message(chat_id, "✅ Пост отправлен в VK!" if success else (error_msg or "❌ Ошибка VK"))
    if file_path and os.path.exists(file_path): os.remove(file_path)
