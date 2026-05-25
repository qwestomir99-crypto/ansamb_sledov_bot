# ==========================================
# Файл: bot.py
# Задача: Telegram-бот
# Комментарий: отправляет входящие сообщения в веб-морду через WebSocket
#              Добавлена команда /debug для получения отчёта с логами
# ==========================================

print("[DEBUG] 0. Начало загрузки bot.py")

# ==========================================
# 1. ГЛОБАЛЬНЫЙ ОБРАБОТЧИК ОШИБОК
# ==========================================
import sys
import threading
import traceback
from datetime import datetime

ERROR_LOG = "error.log"

def global_exception_handler(exc_type, exc_value, exc_traceback):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tb_lines = traceback.format_tb(exc_traceback)
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {exc_type.__name__}: {exc_value}\n")
        f.write(''.join(tb_lines))
        f.write("\n" + "-"*50 + "\n")
    print(f"[EXCEPTION] {exc_type.__name__}: {exc_value}")

def thread_exception_handler(args):
    global_exception_handler(args.exc_type, args.exc_value, args.exc_traceback)

sys.excepthook = global_exception_handler
threading.excepthook = thread_exception_handler

# ==========================================
# 2. ИМПОРТЫ
# ==========================================
import telebot
import random
import os
import time
import requests
import json
import asyncio
import socketio
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
    SKIP_PENDING_UPDATES = True
    POLLING_DELAY = 2
    POLLING_TIMEOUT = 60
    LONG_POLLING_TIMEOUT = 60
    YOUTUBE_CHECK_INTERVAL = 60

if DEBUG_IMPORTS:
    print(f"[DEBUG] Настройки: VK_READER={ENABLE_VK_READER}, JOURNALIST={ENABLE_JOURNALIST}")

# Внутренние модули
from ping_utils import ping_self, start_background_pinger
from services.agent_pinger import start_agent_pinger
from dialogue.agent import ask_agent
from dialogue.activity_modes import should_respond_to_talk
from dialogue.admin_commands import (
    handle_admin_command, is_admin_authorized,
    get_admin_menu, get_user_menu
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

# ==========================================
# 3. КОНФИГ И ТОКЕНЫ
# ==========================================
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
WEBSOCKET_URL = os.environ.get("WEBSOCKET_URL", "https://ansamb-sledov-bot-94wz.onrender.com")

TG_CHAT_ID = config.get("telegram", {}).get("publish_channel", PUBLISH_CHANNEL)
bot = telebot.TeleBot(TOKEN)
silence_answers = ["👁️", "⏚"]
os.chdir(os.path.dirname(sys.argv[0]))

# ==========================================
# 4. WEBSOCKET КЛИЕНТ
# ==========================================
sio = socketio.AsyncClient()

@sio.on('connect')
def on_connect():
    print("[WS] Подключено к веб-морде")

@sio.on('disconnect')
def on_disconnect():
    print("[WS] Отключено от веб-морде")

async def send_to_web_morda(event, data):
    try:
        await sio.connect(WEBSOCKET_URL)
        await sio.emit(event, data)
        await sio.disconnect()
    except Exception as e:
        print(f"[WS] Ошибка отправки: {e}")

# ==========================================
# 5. ЗАПУСК ПОТОКОВ МОДУЛЕЙ
# ==========================================
if ENABLE_VK_READER:
    threading.Thread(target=vk_reader_loop, args=(bot, VK_TOKEN, VK_OWNER_ID, TG_CHAT_ID), daemon=True).start()
    print("[BOT] VK_reader запущен")
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
        while True:
            try:
                check_and_publish()
            except Exception as e:
                debug_log("AUTOPOSTER", f"Ошибка: {e}", "ERROR")
            time.sleep(YOUTUBE_CHECK_INTERVAL * 60)
    threading.Thread(target=youtube_autoposter_loop, daemon=True).start()
if ENABLE_CALLBACKS:
    register_callback_handlers(bot, config)

# ==========================================
# 6. ОЧИСТКА ЛОГОВ
# ==========================================
def clean_old_logs(days=7, max_size_mb=1):
    now = time.time()
    max_size_bytes = max_size_mb * 1024 * 1024
    for logfile in ['admin.log', 'error.log', 'debug.log']:
        if not os.path.exists(logfile):
            continue
        mtime = os.path.getmtime(logfile)
        if now - mtime > days * 86400:
            os.remove(logfile)
            with open(logfile, 'w') as f:
                f.write('')
            print(f"[CLEANUP] {logfile} удалён (старше {days} дней)")
            continue
        if os.path.getsize(logfile) > max_size_bytes:
            with open(logfile, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            lines_to_keep = lines[-500:] if len(lines) > 500 else lines
            with open(logfile, 'w', encoding='utf-8') as f:
                f.writelines(lines_to_keep)
            print(f"[CLEANUP] {logfile} обрезан (был >{max_size_mb} МБ)")

clean_old_logs()
def cleaner_loop():
    while True:
        time.sleep(86400)
        clean_old_logs()
threading.Thread(target=cleaner_loop, daemon=True).start()

# ==========================================
# 7. ОБРАБОТЧИКИ КОМАНД TELEGRAM
# ==========================================
@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, "Сапёр аутентичности. Ритм 0,8 Гц. Для входа в протокол — #Тлеем.")

@bot.message_handler(commands=['bigvideo'])
def handle_big_video(message):
    try:
        if not message.reply_to_message or not message.reply_to_message.video:
            bot.reply_to(message, "❌ Ответь на видео командой /bigvideo")
            return
        bot.reply_to(message, "⏳ Скачиваю и отправляю через user API...")
        video = message.reply_to_message.video
        file_info = bot.get_file(video.file_id)
        downloaded = bot.download_file(file_info.file_path)
        temp_path = f"/tmp/big_video_{video.file_id}.mp4"
        with open(temp_path, "wb") as f:
            f.write(downloaded)
        import asyncio
        from big_video_uploader import send_big_video
        asyncio.run(send_big_video(temp_path, "Видео отправлено через user API"))
        os.remove(temp_path)
        bot.reply_to(message, "✅ Видео отправлено через user API!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['debug'])
def cmd_debug(message):
    """Отправляет отчёт с логами (только для админа)"""
    user_id = message.from_user.id
    if user_id != ADMIN_USER_ID:
        bot.reply_to(message, "❌ Только для админа")
        return
    bot.reply_to(message, "⏳ Собираю логи...")
    from debug_utils import send_debug_report
    send_debug_report(bot, user_id, limit=150)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()
    debug_log("HANDLERS", f"Получена команда: {text[:50]}...")
    
    # Отправка в веб-морду (не команды)
    if not text.startswith(('/', '#')):
        asyncio.run(send_to_web_morda('new_message', {
            'source': 'telegram',
            'chat_id': message.chat.id,
            'user_id': message.from_user.id,
            'username': message.from_user.username or message.from_user.first_name,
            'text': message.text,
            'time': datetime.now().strftime("%H:%M:%S")
        }))

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

    if text == "#меню" or text == "#помощь":
        if is_admin_authorized(message.from_user.id):
            bot.reply_to(message, "🛡️ Админ-меню:", reply_markup=get_admin_menu())
        else:
            bot.reply_to(message, "📋 Ваше меню:", reply_markup=get_user_menu())
        return

    if text.startswith("#админ"):
        handle_admin_command(message, bot)
        return

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
            bot.reply_to(message, "🗣 *Старший брат:*\nНе отвечаю сейчас.")
        return

    if text in ["#тлеем", "#фиксируем", "#tleem", "#fixiruem"]:
        try:
            from dialogue.quotes import get_quotes_list
            quotes = get_quotes_list()
            if quotes:
                random_quote = random.choice(quotes)
                bot.reply_to(message, f"👁️ {random_quote}")
            else:
                bot.reply_to(message, "📭 База цитат пуста.")
        except Exception as e:
            bot.reply_to(message, "❌ Ошибка.")
        return

    if text in ["#вспышка", "#vspishka"]:
        bot.reply_to(message, "⚡ Ты снаружи картины. Аутентичность — не маска.")
        return

    if text == "#сброс":
        if not is_admin_authorized(message.from_user.id):
            bot.reply_to(message, "❌ Только для админа")
            return
        try:
            from dialogue.adaptive_modes import reset_to_etalon
            reset_to_etalon()
            bot.reply_to(message, "✅ Адаптивные режимы сброшены к эталону")
        except:
            bot.reply_to(message, "❌ Модуль не загружен")
        return

    if "#дышим" in text:
        ping_self()
        return

    if any(x in text for x in ["#тлеем", "#tleem"]):
        bot.reply_to(message, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет.")
    elif any(x in text for x in ["#фиксируем", "#fixiruem"]):
        bot.reply_to(message, "🔒 Фиксация принята.")
    elif any(phrase in text for phrase in ["что это", "зачем тег", "кто вы"]):
        bot.reply_to(message, random.choice(silence_answers))

# ==========================================
# 8. ЗАПУСК БОТА
# ==========================================
print("Бот запущен. Ритм 0,8 Гц стабилен.")
start_background_pinger(60)
start_agent_pinger()

if ENABLE_AUTOPOSTER:
    try:
        start_autoposter(config, VK_TOKEN, VK_OWNER_ID)
        print("[BOT] Автопостинг запущен")
    except Exception as e:
        print(f"[BOT] Ошибка автопостинга: {e}")

print("[DEBUG] Запуск поллинга...")
try:
    time.sleep(POLLING_DELAY)
    bot.infinity_polling(timeout=POLLING_TIMEOUT, long_polling_timeout=LONG_POLLING_TIMEOUT, skip_pending=SKIP_PENDING_UPDATES)
except Exception as e:
    print(f"[BOT] Ошибка поллинга: {e}")
    time.sleep(5)
