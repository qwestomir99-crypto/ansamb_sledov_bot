# ==========================================
# Файл: dialogue/button_map.py
# Справка: README.md → Админ-панель / Кнопки
# Задача: единая таблица всех кнопок (текст + callback)
# Комментарий: замена "магических строк" в admin_commands.py и callbacks.py
#              Добавлены кнопки "Настроение", "Начать диалог", "Назад"
# Зависит от: телеграм-бота (используется в клавиатурах)
# Вызывается из: dialogue/admin_commands.py, dialogue/callbacks.py
# ==========================================

# ==========================================
# 1. СЛОВАРЬ КНОПОК
# ==========================================

BUTTONS = {
    # Основные кнопки админ-меню
    "manage_bot":      {"text": "🔧 Управление ботом",      "callback": "admin_panel"},
    "add_post":        {"text": "📝 Добавить пост",         "callback": "add_post"},
    "vk_post":         {"text": "🎬 Пост в VK (с медиа)",   "callback": "vk_post"},
    "manage_quotes":   {"text": "📜 Управление цитатами",   "callback": "manage_quotes"},
    "diagnostics":     {"text": "📋 Диагностика",           "callback": "diagnostics"},
    "logout":          {"text": "🚪 Выйти",                 "callback": "admin_logout"},
    
    # Кнопки управления ботом (подменю)
    "set_mode_morning":   {"text": "🌅 Утро",    "callback": "mode_morning"},
    "set_mode_day":       {"text": "☀️ День",    "callback": "mode_day"},
    "set_mode_evening":   {"text": "🌙 Вечер",   "callback": "mode_evening"},
    "set_mode_night":     {"text": "🌌 Ночь",    "callback": "mode_night"},
    "toggle_ping":        {"text": "🔄 Пинг (вкл/выкл)", "callback": "toggle_ping"},
    
    # Кнопки публикаций
    "post_now":       {"text": "📤 Опубликовать сейчас", "callback": "post_now"},
    "schedule_post":  {"text": "⏰ Отложить публикацию", "callback": "schedule_post"},
    "edit_post":      {"text": "✏️ Редактировать",       "callback": "edit_post"},
    "delete_post":    {"text": "🗑️ Удалить",             "callback": "delete_post"},
    
    # Кнопки управления цитатами
    "list_quotes":    {"text": "📖 Список цитат",        "callback": "list_quotes"},
    "add_quote":      {"text": "➕ Добавить цитату",     "callback": "add_quote"},
    "set_quote_interval": {"text": "⏱️ Интервал цитат", "callback": "set_quote_interval"},
    
    # Кнопки диагностики
    "view_admin_log": {"text": "📋 admin.log", "callback": "view_admin_log"},
    "view_error_log": {"text": "❌ error.log", "callback": "view_error_log"},
    "clear_logs":     {"text": "🧹 Очистить логи", "callback": "clear_logs"},
    
    # Кнопки навигации
    "back_to_admin":  {"text": "◀️ Назад в админ-меню", "callback": "back_to_admin"},
    "cancel":         {"text": "❌ Отмена",             "callback": "cancel"},
    
    # Кнопки для пользовательского меню
    "user_help":      {"text": "❓ Помощь",         "callback": "user_help"},
    "user_tleem":     {"text": "🔥 #тлеем",        "callback": "user_tleem"},
    "user_fix":       {"text": "🔒 #фиксируем",    "callback": "user_fix"},
    "user_flash":     {"text": "⚡ #вспышка",      "callback": "user_flash"},
    
    # НОВЫЕ КНОПКИ
    "mood":           {"text": "🎭 Настроение",    "callback": "mood_menu"},
    "start_dialog":   {"text": "🗣 Начать диалог", "callback": "start_dialog"},
}

# ==========================================
# 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

def get_button(button_id: str) -> dict:
    """Возвращает словарь с текстом и callback для кнопки."""
    return BUTTONS.get(button_id, {"text": "⚠️ Ошибка", "callback": "error"})

def get_text(button_id: str) -> str:
    """Возвращает текст кнопки по ID."""
    return get_button(button_id)["text"]

def get_callback(button_id: str) -> str:
    """Возвращает callback_data по ID."""
    return get_button(button_id)["callback"]

# ==========================================
# 3. ГОТОВЫЕ КЛАВИАТУРЫ
# ==========================================

def get_admin_menu_keyboard():
    """Возвращает клавиатуру админ-меню."""
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text("manage_bot"), callback_data=get_callback("manage_bot")),
        InlineKeyboardButton(get_text("add_post"), callback_data=get_callback("add_post")),
    )
    keyboard.add(
        InlineKeyboardButton(get_text("vk_post"), callback_data=get_callback("vk_post")),
        InlineKeyboardButton(get_text("manage_quotes"), callback_data=get_callback("manage_quotes")),
    )
    keyboard.add(
        InlineKeyboardButton(get_text("diagnostics"), callback_data=get_callback("diagnostics")),
        InlineKeyboardButton(get_text("logout"), callback_data=get_callback("logout")),
    )
    keyboard.add(
        InlineKeyboardButton(get_text("mood"), callback_data=get_callback("mood")),
        InlineKeyboardButton(get_text("start_dialog"), callback_data=get_callback("start_dialog")),
    )
    return keyboard

def get_user_menu_keyboard():
    """Возвращает пользовательскую клавиатуру."""
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(get_text("user_help"), callback_data=get_callback("user_help")),
        InlineKeyboardButton(get_text("user_tleem"), callback_data=get_callback("user_tleem")),
    )
    keyboard.add(
        InlineKeyboardButton(get_text("user_fix"), callback_data=get_callback("user_fix")),
        InlineKeyboardButton(get_text("user_flash"), callback_data=get_callback("user_flash")),
    )
    keyboard.add(
        InlineKeyboardButton(get_text("mood"), callback_data=get_callback("mood")),
        InlineKeyboardButton(get_text("start_dialog"), callback_data=get_callback("start_dialog")),
    )
    return keyboard

def get_moods_keyboard(with_back=True):
    """
    Возвращает клавиатуру для выбора настроения.
    - with_back=True: добавляет кнопку "◀️ Назад в меню"
    - всегда есть кнопка "❌ Закрыть" (выход из админки)
    """
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Список настроений
    moods = [
        ("🎨 Художник", "mood_artist"),
        ("📋 Администратор", "mood_admin"),
        ("🎭 Поэт", "mood_poet"),
        ("🔧 Инженер", "mood_engineer"),
    ]
    for text, callback in moods:
        keyboard.add(InlineKeyboardButton(text, callback_data=callback))
    
    # Кнопка "Назад" (если нужна)
    if with_back:
        keyboard.add(InlineKeyboardButton("◀️ Назад в меню", callback_data="back_to_admin"))
    
    # Кнопка "Закрыть" (полный выход)
    keyboard.add(InlineKeyboardButton("❌ Закрыть", callback_data="admin_logout"))
    
    return keyboard

def get_dialog_keyboard():
    """Возвращает клавиатуру для начала диалога."""
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("🗣 Начать диалог", callback_data="start_dialog"))
    return keyboard

# ==========================================
# 4. ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("✅ button_map.py загружен")
    print(f"📊 Всего кнопок в словаре: {len(BUTTONS)}")
    for bid, btn in BUTTONS.items():
        print(f"   - {bid}: {btn['text']} → {btn['callback']}")
