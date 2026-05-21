# ==========================================
# Файл: dialogue/admin/callbacks.py
# Справка: README.md → Админка (обработчики кнопок)
# Задача: все handle_callback_* для режимов, пинга, цитат, диагностики и т.д.
# Комментарий: импортируется в admin_commands.py
# ==========================================

from dialogue.admin.auth import is_admin_authorized, log_admin_action
from dialogue.admin.menu import get_admin_menu, get_modes_submenu, get_content_submenu, get_quotes_submenu, get_diagnostic_submenu
from dialogue.admin.quotes_admin import handle_quotes_list, handle_quotes_add_start, handle_quotes_interval, handle_quotes_set_interval
from dialogue.admin.posts import handle_pub_menu, ask_for_post_text, handle_vk_post
from dialogue.admin.diagnostics import handle_errors, handle_log, handle_debug
from dialogue.ping_modes import apply_ping_mode
from dialogue.publisher import load_publications
from dialogue.publisher_utils import get_auto_tags, get_random_quote, post_to_vk
from dialogue.quotes import get_quotes_list, add_quote, get_quotes_interval_minutes, set_quotes_interval_minutes, quotes_loop, load_config as load_cfg
from ping_utils import ping_self
import time

def handle_callback_mode(mode, bot, chat_id, message_id, user_id):
    from dialogue.admin_commands import load_config, save_config
    config = load_config()
    config["force_mode"] = mode
    config["force_mode_until"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_config(config)
    apply_ping_mode()
    log_admin_action(user_id, f"mode {mode}", "success")
    
    greetings = {
        "утро": "🌅 Доброе утро, сапёр. Сеть тлеет.",
        "день": "☀️ Хорошего дня. Не забывай #Тлеем.",
        "вечер": "🌙 Спокойного вечера. Наблюдение продолжается.",
        "ночь": "😴 Режим сна. Старший брат отдыхает."
    }
    
    bot.edit_message_text(
        f"✅ Режим «{mode}» установлен\n\n{greetings.get(mode, '')}",
        chat_id, message_id
    )
    from dialogue.admin_commands import return_to_admin_menu
    return_to_admin_menu(bot, chat_id, message_id, user_id)

def handle_callback_ping(interval, bot, chat_id, message_id, user_id):
    from dialogue.admin_commands import load_config, save_config
    config = load_config()
    if "ping" not in config:
        config["ping"] = {}
    config["ping"]["interval"] = interval
    save_config(config)
    apply_ping_mode()
    log_admin_action(user_id, f"ping {interval}", "success")
    bot.edit_message_text(f"✅ Пинг установлен на {interval} секунд", chat_id, message_id)
    from dialogue.admin_commands import return_to_admin_menu
    return_to_admin_menu(bot, chat_id, message_id, user_id)

def handle_callback_toggle_alisa(bot, chat_id, message_id, user_id):
    from dialogue.admin_commands import load_config, save_config
    config = load_config()
    if "alisa" not in config:
        config["alisa"] = {}
    config["alisa"]["enabled"] = not config["alisa"].get("enabled", True)
    save_config(config)
    
    new_status = "🟢 Старший брат: ВКЛ" if config["alisa"]["enabled"] else "🔴 Старший брат: ВЫКЛ"
    
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(row_width=2)
    brother_button = InlineKeyboardButton(new_status, callback_data="toggle_alisa")
    keyboard.add(
        InlineKeyboardButton("🎛 Режимы", callback_data="submenu_modes"),
        brother_button,
        InlineKeyboardButton("📝 Контент", callback_data="submenu_content"),
        InlineKeyboardButton("📜 Цитаты", callback_data="submenu_quotes"),
        InlineKeyboardButton("🔧 Диагностика", callback_data="submenu_diagnostic"),
        InlineKeyboardButton("🚪 Выйти", callback_data="logout")
    )
    
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard)
    bot.answer_callback_query(call.id, f"Старший брат {'включён' if config['alisa']['enabled'] else 'выключен'}")
