# ==========================================
# Файл: Alice/alice_admin.py
# Справка: README.md → Алиса / Управление через админку
# Задача: управление Алисой через кнопку «Старший брат»
# Комментарий: читает config.json, переключает alice.enabled
# Зависит от: telebot, json, os, debug_utils
# Вызывается из: dialogue/callbacks.py (callback_toggle_alice)
# ==========================================

import os
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from debug_utils import debug_log

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def log_alice_admin(level, message):
    debug_log("ALICE_ADMIN", message, level)

def is_alice_enabled():
    config = load_config()
    return config.get("alice", {}).get("enabled", False)

def toggle_alice(call, bot):
    """
    Включает/выключает Алису через config.json.
    Вызывается из callbacks.py по нажатию кнопки «Старший брат».
    """
    user_id = call.from_user.id
    
    config = load_config()
    if "alice" not in config:
        config["alice"] = {}
    
    # Переключаем статус
    current = config["alice"].get("enabled", False)
    config["alice"]["enabled"] = not current
    save_config(config)
    
    new_status = "включена ✅" if config["alice"]["enabled"] else "выключена ❌"
    log_alice_admin("INFO", f"Алиса переключена: {new_status} (пользователь {user_id})")
    
    # Отвечаем пользователю
    bot.answer_callback_query(call.id, f"Алиса {new_status}")
    
    # Обновляем сообщение (если нужно)
    try:
        bot.edit_message_text(
            f"🛡️ *Админ-панель*\n\nАлиса {new_status}.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_admin_menu_with_alice()
        )
    except:
        pass

def get_admin_menu_with_alice():
    """
    Возвращает админ-меню с кнопкой Алисы.
    Используется в toggle_alice для обновления.
    """
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    alice_status = "✅" if is_alice_enabled() else "❌"
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔧 Управление ботом", callback_data="admin_panel"),
        InlineKeyboardButton("📝 Добавить пост", callback_data="add_post"),
    )
    keyboard.add(
        InlineKeyboardButton("🎬 Пост в VK (с медиа)", callback_data="vk_post"),
        InlineKeyboardButton("📜 Управление цитатами", callback_data="manage_quotes"),
    )
    keyboard.add(
        InlineKeyboardButton(f"Старший брат {alice_status}", callback_data="toggle_alice"),
        InlineKeyboardButton("📋 Диагностика", callback_data="diagnostics"),
    )
    keyboard.add(
        InlineKeyboardButton("🚪 Выйти", callback_data="admin_logout"),
    )
    return keyboard
