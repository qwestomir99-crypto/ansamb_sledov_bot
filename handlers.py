# ==========================================
# Файл: new_debugger/handlers.py
# Справка: README.md → Обработчики команд
# Задача: обработка команд пользователей и админов
# Комментарий: добавлена команда #дебаг для отправки логов дебаггера
# ==========================================

import random
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dialogue.admin_commands import (
    handle_admin_command, is_admin_authorized,
    get_admin_menu, get_user_menu
)
from dialogue.activity_modes import should_respond_to_talk
from dialogue.agent import ask_agent
from debug_utils import debug_log
from ping_utils import ping_self

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_moods_keyboard():
    """Возвращает клавиатуру для выбора настроения"""
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
    """Регистрирует все обработчики команд и сообщений"""

    @bot.message_handler(commands=['start'])
    def send_start(message):
        bot.reply_to(message, "Сапёр аутентичности. Ритм 0,8 Гц. Для входа в протокол — #Тлеем.")

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        text = message.text.lower()
        debug_log("HANDLERS", f"Получена команда: {text[:50]}...")

        # --- ИНТЕРАКТИВНАЯ СПРАВКА # ---
        if text == "#":
            try:
                from dialogue.help_menu import get_help_keyboard
                bot.reply_to(
                    message,
                    "📖 *Справка по командам*\n\nВыберите команду для подробного описания:",
                    reply_markup=get_help_keyboard(),
                    parse_mode='Markdown'
                )
            except ImportError:
                bot.reply_to(message, "❌ Модуль справки не загружен")
            return
        # --- КОНЕЦ СПРАВКИ # ---

        # --- КОМАНДА #дебаг (отправка логов дебаггера) ---
        if text == "#дебаг":
            if not is_admin_authorized(message.from_user.id):
                bot.reply_to(message, "❌ Только для админа")
                return
            
            logs_file = "debug.log"
            if os.path.exists(logs_file):
                try:
                    with open(logs_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    last_lines = lines[-500:] if len(lines) > 500 else lines
                    log_text = "".join(last_lines)
                    if log_text.strip():
                        for i in range(0, len(log_text), 4000):
                            bot.send_message(message.chat.id, f"```\n{log_text[i:i+4000]}\n```", parse_mode='Markdown')
                        bot.reply_to(message, "✅ Логи дебаггера отправлены")
                    else:
                        bot.reply_to(message, "📭 Логи пусты")
                except Exception as e:
                    bot.reply_to(message, f"❌ Ошибка чтения: {e}")
            else:
                bot.reply_to(message, "📭 Файл debug.log не найден")
            return
        # --- КОНЕЦ #дебаг ---

        # --- ТЕСТ YOUTUBE API ---
        if text == "#ютуб_тест":
            try:
                from services.youtube_reader import test_youtube
                bot.send_chat_action(message.chat.id, 'typing')
                success = test_youtube()
                if success:
                    bot.reply_to(message, "✅ YouTube API работает! Последнее видео получено.")
                else:
                    bot.reply_to(message, "❌ YouTube API не отвечает. Проверь ключи и ID канала.")
            except ImportError:
                bot.reply_to(message, "❌ Модуль youtube_reader не загружен")
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка: {e}")
            return
        # --- КОНЕЦ ТЕСТА YOUTUBE ---

        if text == "#меню" or text == "#помощь":
            if is_admin_authorized(message.from_user.id):
                bot.reply_to(message, "🛡️ Админ-меню:", reply_markup=get_admin_menu())
            else:
                bot.reply_to(message, "📋 Ваше меню:", reply_markup=get_user_menu())
            return

        if text.startswith("#админ"):
            handle_admin_command(message, bot)
            return

        # --- ОБРАБОТЧИК #говори (через агента) ---
        if text.startswith("#говори"):
            if not should_respond_to_talk():
                bot.reply_to(message, "🌙 Старший брат отдыхает. Спроси в другой раз.")
                return
            
            phrase = text.replace("#говори", "", 1).strip()
            if not phrase:
                bot.reply_to(message, "🗣 *Старший брат:*\nА что ты хотел сказать?")
                return
            
            bot.send_chat_action(message.chat.id, 'typing')
            answer = ask_agent(phrase)
            
            if answer:
                bot.reply_to(message, f"🗣 *Старший брат:*\n{answer}", parse_mode='Markdown')
            else:
                bot.reply_to(message, "🗣 *Старший брат:*\nНе отвечаю сейчас. Попробуй позже.")
            return
        # --- КОНЕЦ ОБРАБОТЧИКА #говори ---

        # --- РИТУАЛЬНЫЕ КОМАНДЫ (#тлеем, #фиксируем) ---
        if text in ["#тлеем", "#фиксируем", "#tleem", "#fixiruem"]:
            try:
                from dialogue.quotes import get_quotes_list
                quotes = get_quotes_list()
                if quotes:
                    import random
                    random_quote = random.choice(quotes)
                    bot.reply_to(message, f"👁️ {random_quote}")
                else:
                    bot.reply_to(message, "📭 База цитат пуста. Добавьте цитаты через админку.")
            except Exception as e:
                bot.reply_to(message, "❌ Ошибка при выборе цитаты.")
                debug_log("HANDLERS", f"Ошибка: {e}", "ERROR")
            return
        # --- КОНЕЦ РИТУАЛЬНЫХ КОМАНД ---

        # --- КОМАНДА #вспышка ---
        if text in ["#вспышка", "#vspishka"]:
            bot.reply_to(message, "⚡ Ты снаружи картины. До погружения. Аутентичность — не маска. Это способ не сдаться.")
            return
        # --- КОНЕЦ #вспышка ---

        # --- КОМАНДА #сброс (сброс адаптивных режимов к эталону) ---
        if text == "#сброс":
            if not is_admin_authorized(message.from_user.id):
                bot.reply_to(message, "❌ Только для админа")
                return
            try:
                from dialogue.adaptive_modes import reset_to_etalon
                reset_to_etalon()
                bot.reply_to(message, "✅ Адаптивные режимы сброшены к эталону")
                debug_log("HANDLERS", "Выполнен сброс адаптивных режимов")
            except ImportError:
                bot.reply_to(message, "❌ Модуль адаптивных режимов не загружен")
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка сброса: {e}")
            return
        # --- КОНЕЦ #сброс ---

        # --- КОМАНДА #настроение (меню с кнопками) ---
        if text == "#настроение":
            if not is_admin_authorized(message.from_user.id):
                bot.reply_to(message, "❌ Только для админа")
                return
            
            bot.send_message(
                message.chat.id,
                "🎭 *Выбери настроение:*",
                parse_mode='Markdown',
                reply_markup=get_moods_keyboard()
            )
            return
        # --- КОНЕЦ #настроение ---

        if "#дышим" in text:
            ping_self()
            return

        # --- СТАРАЯ СПРАВКА УДАЛЕНА ---
        # Оставлена только интерактивная по команде #

        if any(x in text for x in ["#тлеем", "#tleem"]):
            bot.reply_to(message, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет. Ожидаем #Фиксируем.")
        elif any(x in text for x in ["#фиксируем", "#fixiruem"]):
            bot.reply_to(message, "🔒 Фиксация принята. Ритм 0,8 Гц подтверждён. Сеть тлеет.")
        elif any(x in text for x in ["#вспышка", "#vspishka"]):
            bot.reply_to(message, "💥 Импульс зафиксирован. Синхронизация завершена. QSL.")
        elif any(phrase in text for phrase in ["что это", "зачем тег", "кто вы", "что за ритуал"]):
            bot.reply_to(message, random.choice(silence_answers))
