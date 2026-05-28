# ==========================================
# Файл: dialogue/track_commands.py
# Справка: README.md → Команды для артефактов
# Задача: обработчики команд #трек, #картина, #сценарий для бота
# Комментарий: вызывает tracking.py и возвращает ссылку
# Зависит от: telebot, tracking, debug_utils
# Вызывается из: bot.py (handle_message)
# ==========================================

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.tracking import track_track, track_picture, track_blueprint
from debug_utils import debug_log

def log_tc(level, message):
    debug_log("TRACK_COMMANDS", message, level)

# ==========================================
# 1. ОБРАБОТЧИКИ КОМАНД
# ==========================================
def handle_track_command(bot, message, command, query, track_func):
    """Общая функция для обработки команд артефактов"""
    url = track_func(query)
    if not url:
        bot.reply_to(message, f"❌ Артефакт '{query}' не найден")
        return
    
    # Формируем клавиатуру для отправки
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔗 Перейти", url=url))
    
    # Отправляем сообщение
    bot.reply_to(
        message,
        f"🔗 *{command.upper()}*: {query}\n\n[Нажмите для перехода]({url})",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    log_tc("INFO", f"Отправлен артефакт '{query}' по команде {command}")

# ==========================================
# 2. КОНКРЕТНЫЕ ОБРАБОТЧИКИ
# ==========================================
def handle_track_track(bot, message, query):
    handle_track_command(bot, message, "#трек", query, track_track)

def handle_track_picture(bot, message, query):
    handle_track_command(bot, message, "#картина", query, track_picture)

def handle_track_blueprint(bot, message, query):
    handle_track_command(bot, message, "#сценарий", query, track_blueprint)

# ==========================================
# 3. ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ КОМАНД ===")
    print("Файл загружен")
