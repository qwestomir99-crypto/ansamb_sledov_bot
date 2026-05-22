# ==========================================
# Файл: dialogue/admin/menu.py
# Задача: формирование меню админки (кнопки)
# Комментарий: добавлены адаптивные режимы и разделение Старшего брата на вкл/выкл
# ==========================================

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_menu():
    """Главное меню админки"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🤖 Управление ботом", callback_data="submenu_modes"),
        InlineKeyboardButton("🧠 Адаптивные режимы", callback_data="submenu_adaptive"),
        InlineKeyboardButton("📝 Публикации", callback_data="submenu_content"),
        InlineKeyboardButton("➕ Добавить пост", callback_data="add_post"),
        InlineKeyboardButton("🎬 Пост в VK (с медиа)", callback_data="vk_post"),
        InlineKeyboardButton("📜 Управление цитатами", callback_data="submenu_quotes"),
        InlineKeyboardButton("🔧 Диагностика", callback_data="submenu_diagnostic"),
        InlineKeyboardButton("🐞 Дебаггер", callback_data="debugger_menu"),
        InlineKeyboardButton("🚪 Выйти", callback_data="logout")
    )
    return markup

def get_user_menu():
    """Меню для обычного пользователя"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💥 #тлеем", callback_data="tleem"),
        InlineKeyboardButton("🔒 #фиксируем", callback_data="fixiruem"),
        InlineKeyboardButton("⚡ #вспышка", callback_data="vspishka"),
        InlineKeyboardButton("🌬 #дышим", callback_data="dyshim"),
        InlineKeyboardButton("🗣 #говори", callback_data="govorim"),
        InlineKeyboardButton("📖 Справка", callback_data="help")
    )
    return markup

def get_modes_submenu():
    """Подменю управления режимами и пингом (Старший брат — две кнопки)"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌅 Утро", callback_data="mode_утро"),
        InlineKeyboardButton("☀️ День", callback_data="mode_день"),
        InlineKeyboardButton("🌙 Вечер", callback_data="mode_вечер"),
        InlineKeyboardButton("🌌 Ночь", callback_data="mode_ночь"),
        InlineKeyboardButton("✅ Вкл. Старший брат", callback_data="toggle_alisa_on"),
        InlineKeyboardButton("❌ Выкл. Старший брат", callback_data="toggle_alisa_off"),
        InlineKeyboardButton("🕒 Пинг 30", callback_data="ping_30"),
        InlineKeyboardButton("🕒 Пинг 60", callback_data="ping_60"),
        InlineKeyboardButton("🕒 Пинг 180", callback_data="ping_180"),
        InlineKeyboardButton("◀️ Назад", callback_data="admin_menu")
    )
    return markup

def get_adaptive_submenu():
    """Подменю управления адаптивными режимами"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Включить адаптивку", callback_data="adaptive_enable"),
        InlineKeyboardButton("❌ Выключить адаптивку", callback_data="adaptive_disable"),
        InlineKeyboardButton("📊 Сброс к эталону", callback_data="adaptive_reset"),
        InlineKeyboardButton("◀️ Назад", callback_data="admin_menu")
    )
    return markup

def get_content_submenu():
    """Подменю управления контентом"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📝 Список публикаций", callback_data="pub_menu"),
        InlineKeyboardButton("➕ Добавить пост", callback_data="add_post"),
        InlineKeyboardButton("◀️ Назад", callback_data="admin_menu")
    )
    return markup

def get_quotes_submenu():
    """Подменю управления цитатами"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📜 Список цитат", callback_data="quotes_list"),
        InlineKeyboardButton("➕ Добавить цитату", callback_data="quotes_add"),
        InlineKeyboardButton("⏱ Интервал цитат", callback_data="quotes_interval"),
        InlineKeyboardButton("◀️ Назад", callback_data="admin_menu")
    )
    return markup

def get_diagnostic_submenu():
    """Подменю диагностики"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("❌ Ошибки", callback_data="errors"),
        InlineKeyboardButton("📋 Лог", callback_data="log"),
        InlineKeyboardButton("🕯 Шаббат", callback_data="shabbat_info"),
        InlineKeyboardButton("◀️ Назад", callback_data="admin_menu")
    )
    return markup

def get_debugger_menu():
    """Меню дебаггера"""
    from debug_utils import load_config
    config = load_config()
    enabled = config.get("enabled", True)
    interval = config.get("interval_minutes", 5)
    send_to_tg = config.get("send_to_telegram", True)
    
    status_icon = "✅" if enabled else "❌"
    send_icon = "✅" if send_to_tg else "❌"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{status_icon} Дебаггер", callback_data="debugger_enable" if not enabled else "debugger_disable"),
        InlineKeyboardButton(f"⏱ Интервал ({interval} мин)", callback_data="debugger_interval"),
        InlineKeyboardButton(f"{send_icon} Отправка в Telegram", callback_data="debugger_toggle_send"),
        InlineKeyboardButton("📋 Модули", callback_data="debugger_modules"),
        InlineKeyboardButton("📤 Логи", callback_data="debugger_logs"),
        InlineKeyboardButton("◀️ Назад", callback_data="admin_menu")
    )
    return markup
