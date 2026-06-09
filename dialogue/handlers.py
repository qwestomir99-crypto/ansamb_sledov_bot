# ==========================================
# Модуль: dialogue/handlers.py
# Справка: README.md → Обработчики команд
# Задача: обработка команд пользователей и админов
# Зависит от: admin_commands.py, activity_modes.py, agent.py
# Вызывается из: bot.py
# ==========================================

import os
import random
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.admin_commands import (
    handle_admin_command, is_admin_authorized,
    get_admin_menu, get_user_menu
)
from dialogue.activity_modes import should_respond_to_talk
from dialogue.agent import ask_agent
from debug_utils import debug_log
from ping_utils import ping_self

# Путь к файлу конфигурации
CONFIG_FILE = os.path.join('dialogue', 'data', 'config.json')

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_moods_keyboard():
    from dialogue.user_settings import MOODS
    keyboard = InlineKeyboardMarkup(row_width=2)
    for mood_id, mood_data in MOODS.items():
        keyboard.add(InlineKeyboardButton(
            f"{mood_data['emoji']} {mood_data['name']}",
            callback_data=f"set_mood_{mood_id}"
        ))
    keyboard.add(InlineKeyboardButton("❌ Закрыть", callback_data="close_mood_menu"))
    return keyboard

silence_answers = ["👁️", "⏚"]

def register_handlers(bot, config):

    @bot.message_handler(commands=['start'])
    def send_start(message):
        bot.reply_to(message, "Сапёр аутентичности. Ритм 0,8 Гц. Для входа в протокол — #Тлеем.")

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        text = message.text or ""
        text_lower = text.lower()
        
        debug_log("HANDLERS", f"v2 | {text[:50]}")

        if text == "#":
            try:
                from dialogue.help_menu import get_help_keyboard
                bot.reply_to(message, "📖 *Справка*", reply_markup=get_help_keyboard(), parse_mode='Markdown')
            except:
                bot.reply_to(message, "❌ Модуль справки не загружен")
            return

        if text_lower in ["#меню", "#помощь"]:
            if is_admin_authorized(message.from_user.id):
                bot.reply_to(message, "🛡️ Админ-меню:", reply_markup=get_admin_menu())
            else:
                bot.reply_to(message, "📋 Ваше меню:", reply_markup=get_user_menu())
            return

        if text_lower.startswith("#админ"):
            handle_admin_command(message, bot)
            return

        if text_lower.startswith("#говори"):
            if not should_respond_to_talk():
                bot.reply_to(message, "🌙 Старший брат отдыхает.")
                return
            phrase = text[6:].strip()
            if not phrase:
                bot.reply_to(message, "🗣 А что ты хотел сказать?")
                return
            bot.send_chat_action(message.chat.id, 'typing')
            answer = ask_agent(phrase)
            if answer:
                bot.reply_to(message, f"🗣 *Старший брат:*\n{answer}", parse_mode='Markdown')
            else:
                bot.reply_to(message, "🗣 Не отвечаю сейчас.")
            return

        if text_lower in ["#тлеем", "#фиксируем", "#tleem", "#fixiruem"]:
            try:
                from dialogue.quotes import get_quotes_list
                quotes = get_quotes_list()
                if quotes:
                    bot.reply_to(message, f"👁️ {random.choice(quotes)}")
                else:
                    bot.reply_to(message, "📭 База цитат пуста.")
            except:
                bot.reply_to(message, "❌ Ошибка.")
            return

        if text_lower in ["#вспышка", "#vspishka"]:
            bot.reply_to(message, "⚡ Ты снаружи картины.")
            return

        if text_lower == "#сброс":
            if not is_admin_authorized(message.from_user.id):
                bot.reply_to(message, "❌ Только для админа")
                return
            try:
                from dialogue.adaptive_modes import reset_to_etalon
                reset_to_etalon()
                bot.reply_to(message, "✅ Сброшено.")
            except:
                bot.reply_to(message, "❌ Ошибка.")
            return

        if text_lower == "#настроение":
            if not is_admin_authorized(message.from_user.id):
                bot.reply_to(message, "❌ Только для админа")
                return
            bot.send_message(message.chat.id, "🎭 *Выбери настроение:*", parse_mode='Markdown', reply_markup=get_moods_keyboard())
            return

        if "#дышим" in text_lower:
            ping_self()
            return

        if text_lower == "#ютуб_тест":
            try:
                from services.youtube_reader import test_youtube
                bot.send_chat_action(message.chat.id, 'typing')
                if test_youtube():
                    bot.reply_to(message, "✅ YouTube API работает!")
                else:
                    bot.reply_to(message, "❌ YouTube API не отвечает.")
            except:
                bot.reply_to(message, "❌ Ошибка.")
            return

        if any(phrase in text_lower for phrase in ["что это", "зачем тег", "кто вы", "что за ритуал"]):
            bot.reply_to(message, random.choice(silence_answers))
