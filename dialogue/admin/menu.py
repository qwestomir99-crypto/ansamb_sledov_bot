# ==========================================
# Файл: new_debugger/dialogue/admin/menu.py
# Справка: README.md → Админка (меню)
# Задача: все функции для построения кнопок и подменю
# Комментарий: добавлено подменю дебаггера и кнопка Шаббата в диагностике
# ==========================================

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.admin_commands import load_config
from debug_utils import load_config as load_debug_config

def get_admin_menu():
    """Главное админ-меню (2 колонки) с динамической кнопкой Старший брат"""
    config = load_config()
    alisa_enabled = config.get("alisa", {}).get("enabled", True)
    
    if alisa_enabled:
        brother_button = InlineKeyboardButton("🟢 Старший брат: ВКЛ", callback_data="toggle_alisa")
    else:
        brother_button = InlineKeyboardButton("🔴 Старший брат: ВЫКЛ", callback_data="toggle_alisa")
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🎛 Режимы", callback_data="submenu_modes"),
        brother_button,
        InlineKeyboardButton("📝 Контент", callback_data="submenu_content"),
        InlineKeyboardButton("📜 Цитаты", callback_data="submenu_quotes"),
        InlineKeyboardButton("🔧 Диагностика", callback_data="submenu_diagnostic"),
        InlineKeyboardButton("🐞 Дебаггер", callback_data="debugger_menu"),
        InlineKeyboardButton("🚪 Выйти", callback_data="logout")
    )
    return keyboard

def get_modes_submenu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🌅 Утро", callback_data="mode_утро"),
        InlineKeyboardButton("☀️ День", callback_data="mode_день"),
        InlineKeyboardButton("🌙 Вечер", callback_data="mode_вечер"),
        InlineKeyboardButton("😴 Ночь", callback_data="mode_ночь"),
        InlineKeyboardButton("⏱ 30", callback_data="ping_30"),
        InlineKeyboardButton("⏱ 60", callback_data="ping_60"),
        InlineKeyboardButton("⏱ 180", callback_data="ping_180")
    )
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="admin_menu"))
    return keyboard

def get_content_submenu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📤 Публикации", callback_data="pub_menu"),
        InlineKeyboardButton("➕ Добавить пост", callback_data="add_post"),
        InlineKeyboardButton("🎬 Пост в VK", callback_data="vk_post")
    )
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="admin_menu"))
    return keyboard

def get_quotes_submenu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📋 Список", callback_data="quotes_list"),
        InlineKeyboardButton("➕ Добавить", callback_data="quotes_add"),
        InlineKeyboardButton("⏱ Интервал", callback_data="quotes_interval")
    )
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="admin_menu"))
    return keyboard

def get_diagnostic_submenu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📋 Ошибки", callback_data="errors"),
        InlineKeyboardButton("📜 Лог", callback_data="log"),
        InlineKeyboardButton("🐞 Дебаг", callback_data="debug"),
        InlineKeyboardButton("🕯 Шаббат", callback_data="shabbat_info")
    )
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="admin_menu"))
    return keyboard

def get_user_menu():
    """Пользовательское меню (для неавторизованных)"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💥 #Тлеем", callback_data="tleem"),
        InlineKeyboardButton("🔒 #Фиксируем", callback_data="fixiruem"),
        InlineKeyboardButton("⚡ #Вспышка", callback_data="vspishka"),
        InlineKeyboardButton("🌬 #дышим", callback_data="dyshim"),
        InlineKeyboardButton("🗣 #говорим", callback_data="govorim"),
        InlineKeyboardButton("📖 #справка", callback_data="help")
    )
    return keyboard

# ==========================================
# Меню дебаггера
# ==========================================

def get_debugger_menu():
    """Подменю для управления дебаггером (с отдельными кнопками Вкл/Выкл)"""
    config = load_debug_config()
    
    interval = config.get("interval_minutes", 0)
    interval_text = "сразу" if interval == 0 else f"каждые {interval} мин"
    send_enabled = config.get("send_to_telegram", True)
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🟢 Включить дебаггер", callback_data="debugger_enable"),
        InlineKeyboardButton("🔴 Выключить дебаггер", callback_data="debugger_disable")
    )
    keyboard.add(
        InlineKeyboardButton(f"⏱ Интервал: {interval_text}", callback_data="debugger_interval"),
        InlineKeyboardButton(f"📤 Telegram: {'✅ Вкл' if send_enabled else '❌ Выкл'}", callback_data="debugger_toggle_send")
    )
    keyboard.add(
        InlineKeyboardButton("📋 Выбрать модули", callback_data="debugger_modules"),
        InlineKeyboardButton("📊 Последние логи", callback_data="debugger_logs"),
        InlineKeyboardButton("◀️ Назад", callback_data="admin_menu")
    )
    return keyboard
