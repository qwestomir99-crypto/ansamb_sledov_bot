# ==========================================
# Файл: dialogue/admin/quotes_admin.py
# Справка: README.md → Админка (управление цитатами)
# Задача: обработчики кнопок для цитат (список, добавление, интервал)
# Комментарий: вызывается из callbacks.py
# ==========================================

import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.quotes import (
    get_quotes_list, add_quote, get_quotes_interval_minutes,
    set_quotes_interval_minutes, quotes_loop, load_config as load_cfg
)
from dialogue.admin.auth import log_admin_action

def handle_quotes_list(bot, chat_id, message_id, user_id):
    quotes = get_quotes_list()
    if not quotes:
        bot.edit_message_text("📭 Список цитат пуст", chat_id, message_id)
        return
    
    text = "📜 *Список цитат:*\n\n"
    for i, q in enumerate(quotes):
        text += f"`{i+1}.` {q[:60]}{'...' if len(q) > 60 else ''}\n"
        if len(text) > 3500:
            bot.send_message(user_id, text, parse_mode='Markdown')
            text = ""
    
    if text:
        bot.edit_message_text(text, chat_id, message_id, parse_mode='Markdown')

def handle_quotes_add_start(bot, chat_id, message_id, user_id):
    msg = bot.send_message(chat_id, "✍️ Введите текст новой цитаты:")
    bot.register_next_step_handler(msg, process_quote_add, bot, chat_id, user_id)

def process_quote_add(message, bot, chat_id, user_id):
    text = message.text.strip()
    if not text:
        bot.send_message(chat_id, "❌ Цитата не может быть пустой")
    else:
        add_quote(text)
        log_admin_action(user_id, f"add_quote: {text[:50]}", "success")
        bot.send_message(chat_id, f"✅ Цитата добавлена:\n\n{text}")

def handle_quotes_interval(bot, chat_id, message_id, user_id):
    current = get_quotes_interval_minutes()
    keyboard = InlineKeyboardMarkup(row_width=3)
    for minutes in [15, 30, 60, 120, 240, 480]:
        marker = "✅" if minutes == current else ""
        keyboard.add(InlineKeyboardButton(f"{minutes} мин {marker}", callback_data=f"quote_int_{minutes}"))
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="submenu_quotes"))
    bot.edit_message_text(
        f"⏱ *Интервал публикации цитат*\n\nТекущий: {current} минут\n\nВыбери новый:",
        chat_id, message_id, parse_mode='Markdown', reply_markup=keyboard
    )

def handle_quotes_set_interval(interval, bot, chat_id, message_id, user_id):
    set_quotes_interval_minutes(interval)
    import dialogue.quotes as quotes_module
    quotes_module.quote_thread_running = False
    time.sleep(1)
    cfg = load_cfg()
    TG_CHAT_ID = cfg.get("telegram", {}).get("publish_channel", "@qwestomir")
    quotes_module.quotes_loop(bot, TG_CHAT_ID)
    log_admin_action(user_id, f"quotes_interval {interval}", "success")
    bot.edit_message_text(f"✅ Интервал цитат установлен: {interval} минут", chat_id, message_id)
