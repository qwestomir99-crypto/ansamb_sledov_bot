# ==========================================
# Файл: bot.py
# Справка: README.md → Главный модуль
# Задача: точка входа, запуск потоков, команды
# Комментарий: Flask вынесен в services/web_server.py
# ==========================================

print("[DEBUG] 0. Начало загрузки bot.py")

import telebot
import random
import os
import sys
import threading
import time
import traceback
import requests
import json
from datetime import datetime

# Настройки
try:
    from settings import *
    print("[DEBUG] Настройки загружены из settings.py")
except ImportError:
    print("[DEBUG] settings.py не найден, использую значения по умолчанию")
    ENABLE_VK_READER = True
    ENABLE_JOURNALIST = True
    ENABLE_QUOTES = True
    ENABLE_SCHEDULER = True
    ENABLE_PUBLISHER = True
    ENABLE_AUTOPOSTER = True
    ENABLE_CALLBACKS = True
    ENABLE_ALISA = False
    DEBUG_IMPORTS = True
    DEBUG_THREADS = True
    SKIP_PENDING_UPDATES = True
    POLLING_DELAY = 2
    POLLING_TIMEOUT = 60
    LONG_POLLING_TIMEOUT = 60
    YOUTUBE_CHECK_INTERVAL = 60

if DEBUG_IMPORTS:
    print(f"[DEBUG] Настройки: VK_READER={ENABLE_VK_READER}, JOURNALIST={ENABLE_JOURNALIST}, QUOTES={ENABLE_QUOTES}")

# Импорт модулей
from ping_utils import ping_self, start_background_pinger
from services.agent_pinger import start_agent_pinger
from services.web_server import run_flask
from dialogue.agent import ask_agent
from dialogue.activity_modes import should_respond_to_talk
from dialogue.admin_commands import (
    handle_admin_command, is_admin_authorized,
    get_admin_menu, get_user_menu,
    ask_for_post_text
)
from debug_utils import debug_log

if ENABLE_JOURNALIST:
    from dialogue.journalist import journalist_loop
if ENABLE_VK_READER:
    from dialogue.vk_reader import vk_reader_loop
if ENABLE_QUOTES:
    from dialogue.quotes import quotes_loop
if ENABLE_PUBLISHER:
    from dialogue.publisher import publish_loop
if ENABLE_SCHEDULER:
    from dialogue.scheduler import scheduler_loop
if ENABLE_AUTOPOSTER:
    from services.autoposter import start_autoposter, check_and_publish
if ENABLE_CALLBACKS:
    from dialogue.callbacks import register_callback_handlers

# Загрузка конфига
CONFIG_FILE = "config.json"
def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не задан")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))
VK_TOKEN = os.environ.get("VK_TOKEN")
VK_OWNER_ID = os.environ.get("VK_OWNER_ID")
PUBLISH_CHANNEL = os.environ.get("PUBLISH_CHANNEL", "@qwestomir")
AGENT_URL = os.environ.get("AGENT_URL", "https://agent-3kek.onrender.com/ask")

TG_CHAT_ID = config.get("telegram", {}).get("publish_channel", PUBLISH_CHANNEL)
bot = telebot.TeleBot(TOKEN)
silence_answers = ["👁️", "⏚"]
os.chdir(os.path.dirname(sys.argv[0]))

# Запуск Flask
threading.Thread(target=run_flask, daemon=True).start()

# Пинг для keep-alive
def keep_alive():
    while True:
        time.sleep(60)
        try:
            requests.get('http://127.0.0.1:10000/')
        except:
            pass
threading.Thread(target=keep_alive, daemon=True).start()

# Очистка логов
def clean_old_logs(days=7):
    now = time.time()
    for logfile in ['admin.log', 'error.log']:
        if os.path.exists(logfile):
            mtime = os.path.getmtime(logfile)
            if now - mtime > days * 86400:
                os.remove(logfile)
                with open(logfile, 'w') as f:
                    f.write('')
clean_old_logs()
threading.Thread(target=lambda: [time.sleep(86400) or clean_old_logs() for _ in range(999)], daemon=True).start()

# Потоки модулей
if ENABLE_VK_READER:
    threading.Thread(target=vk_reader_loop, args=(bot, VK_TOKEN, VK_OWNER_ID, TG_CHAT_ID), daemon=True).start()
if ENABLE_JOURNALIST:
    threading.Thread(target=journalist_loop, args=(bot, TG_CHAT_ID), daemon=True).start()
if ENABLE_QUOTES:
    threading.Thread(target=quotes_loop, args=(bot, TG_CHAT_ID), daemon=True).start()
if ENABLE_SCHEDULER:
    threading.Thread(target=scheduler_loop, args=(bot, TG_CHAT_ID), daemon=True).start()
if ENABLE_PUBLISHER:
    threading.Thread(target=publish_loop, args=(bot, VK_TOKEN, VK_OWNER_ID, TG_CHAT_ID), daemon=True).start()

if ENABLE_AUTOPOSTER:
    def youtube_autoposter_loop():
        interval_minutes = YOUTUBE_CHECK_INTERVAL
        interval_seconds = interval_minutes * 60
        time.sleep(30)
        while True:
            try:
                check_and_publish()
            except Exception as e:
                debug_log("AUTOPOSTER", f"Ошибка в цикле: {e}", "ERROR")
            time.sleep(interval_seconds)
    threading.Thread(target=youtube_autoposter_loop, daemon=True).start()

if ENABLE_CALLBACKS:
    register_callback_handlers(bot, config)

# ------------------------------------------------------------
# Обработчики команд
# ------------------------------------------------------------
@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, "Сапёр аутентичности. Ритм 0,8 Гц. Для входа в протокол — #Тлеем.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()
    debug_log("HANDLERS", f"Получена команда: {text[:50]}...")

    # Интерактивная справка #
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

    # Меню / Помощь
    if text == "#меню" or text == "#помощь":
        if is_admin_authorized(message.from_user.id):
            bot.reply_to(message, "🛡️ Админ-меню:", reply_markup=get_admin_menu())
        else:
            bot.reply_to(message, "📋 Ваше меню:", reply_markup=get_user_menu())
        return

    # Админ-вход
    if text.startswith("#админ"):
        handle_admin_command(message, bot)
        return

    # Говори
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

    # Ритуальные команды (#тлеем, #фиксируем)
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

    # Вспышка
    if text in ["#вспышка", "#vspishka"]:
        bot.reply_to(message, "⚡ Ты снаружи картины. До погружения. Аутентичность — не маска. Это способ не сдаться.")
        return

    # Сброс адаптивных режимов
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

    # Настроение (меню с кнопками)
    if text == "#настроение":
        if not is_admin_authorized(message.from_user.id):
            bot.reply_to(message, "❌ Только для админа")
            return
        from dialogue.user_settings import get_moods_keyboard
        bot.send_message(
            message.chat.id,
            "🎭 *Выбери настроение:*",
            parse_mode='Markdown',
            reply_markup=get_moods_keyboard()
        )
        return

    # Дышим
    if "#дышим" in text:
        ping_self()
        return

    # Обработка фраз
    if any(x in text for x in ["#тлеем", "#tleem"]):
        bot.reply_to(message, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет. Ожидаем #Фиксируем.")
    elif any(x in text for x in ["#фиксируем", "#fixiruem"]):
        bot.reply_to(message, "🔒 Фиксация принята. Ритм 0,8 Гц подтверждён. Сеть тлеет.")
    elif any(x in text for x in ["#вспышка", "#vspishka"]):
        bot.reply_to(message, "💥 Импульс зафиксирован. Синхронизация завершена. QSL.")
    elif any(phrase in text for phrase in ["что это", "зачем тег", "кто вы", "что за ритуал"]):
        bot.reply_to(message, random.choice(silence_answers))

# Запуск
print("Бот запущен. Ритм 0,8 Гц стабилен. Ожидаем #Тлеем...")
start_background_pinger(60)
start_agent_pinger()

if ENABLE_AUTOPOSTER:
    try:
        start_autoposter(config, VK_TOKEN, VK_OWNER_ID)
        print("[BOT] Автопостинг (старая версия) запущен")
    except Exception as e:
        print(f"[BOT] Ошибка автопостинга: {e}")

print("[DEBUG] 7. Запуск поллинга...")
try:
    time.sleep(POLLING_DELAY)
    bot.infinity_polling(timeout=POLLING_TIMEOUT, long_polling_timeout=LONG_POLLING_TIMEOUT, skip_pending=SKIP_PENDING_UPDATES)
except Exception as e:
    print(f"[BOT] Ошибка поллинга: {e}")
    time.sleep(5)
