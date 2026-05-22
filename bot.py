# ==========================================
# Файл: bot.py
# Задача: главный бот (Flask + Telegram)
# Комментарий: добавлен временный маршрут /new для показа новой веб-морды
#              из папки new_debugger/templates/admin.html
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
from flask import Flask, request

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

# ==========================================
# Flask-сервер (старый, keep-alive)
# ==========================================
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    if request.remote_addr == '127.0.0.1':
        return "Pong", 200
    return {"status": "tleem", "rhythm": "0.8 Hz", "version": "3.2"}, 200

@flask_app.route('/token', methods=['GET'])
def get_token():
    secret = request.args.get('secret')
    if secret != os.environ.get("TOKEN_SECRET", "tleem2026"):
        return "Forbidden", 403
    return TOKEN, 200

@flask_app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

# ==========================================
# НОВЫЙ МАРШРУТ /new — показывает новую веб-морду
# ==========================================
@flask_app.route('/new')
def new_web_morda():
    """Временный маршрут для новой веб-морды из new_debugger/templates/admin.html"""
    from pathlib import Path
    
    # Ищем admin.html в new_debugger/templates/
    base_path = Path(__file__).parent
    html_path = base_path / "admin.html"
    
    if not html_path.exists():
        return f"""
        <html>
            <body style="background:#0a0a0a; color:#ff4444; font-family:monospace; padding:2rem;">
                <h2>❌ admin.html не найден</h2>
                <p>Искали: {html_path}</p>
                <p>Текущая директория: {Path.cwd()}</p>
                <hr>
                <p>Убедись, что файл существует:<br>
                <code>new_debugger/templates/admin.html</code></p>
                <p>Содержимое папки new_debugger/templates/:</p>
                <pre>{list((base_path / "new_debugger" / "templates").iterdir()) if (base_path / "new_debugger" / "templates").exists() else "папка не существует"}</pre>
            </body>
        </html>
        """, 404
    
    html_content = html_path.read_text(encoding='utf-8')
    
    # Простая замена переменных (без Jinja2)
    html_content = html_content.replace("{{ mode }}", "🌙 тестовый режим (Flask-костыль)")
    html_content = html_content.replace("{{ time }}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Замена цитат на тестовые
    test_quotes_html = '<li>«Сеть тлеет. Ритм 0,8 Гц.»</li><li>«Сапёр аутентичности на связи.»</li><li>«Ты — тень. Бот — голос.»</li>'
    
    if '<ul id="quotes-list">' in html_content:
        import re
        html_content = re.sub(
            r'(<ul id="quotes-list">).*?(</ul>)',
            rf'\1{test_quotes_html}\2',
            html_content,
            flags=re.DOTALL
        )
    
    return html_content

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False)

# ==========================================
# Запуск Flask в потоке
# ==========================================
threading.Thread(target=run_flask, daemon=True).start()
print("[BOT] 🔧 Flask-сервер (keep-alive) запущен")

# ==========================================
# Очистка логов
# ==========================================
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

# ==========================================
# Потоки модулей
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

# ==========================================
# Ожидание готовности агента
# ==========================================
def wait_for_agent():
    agent_url = "https://agent-3kek.onrender.com/health"
    print("[BOT] Ожидание готовности агента...")
    for attempt in range(30):
        try:
            r = requests.get(agent_url, timeout=2)
            if r.status_code == 200:
                print("[BOT] ✅ Агент готов")
                return True
        except:
            pass
        print(f"[BOT] Ожидание агента, попытка {attempt+1}/30")
        time.sleep(2)
    print("[BOT] ⚠️ Агент не ответил, продолжаем без него")
    return False

wait_for_agent()

# ==========================================
# Обработчики команд
# ==========================================
@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, "Сапёр аутентичности. Ритм 0,8 Гц. Для входа в протокол — #Тлеем.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()
    debug_log("HANDLERS", f"Получена команда: {text[:50]}...")

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
            bot.reply_to(message, "🗣 *Старший брат:*\nНе отвечаю сейчас. Попробуй позже.")
        return

    if text in ["#тлеем", "#фиксируем", "#tleem", "#fixiruem"]:
        try:
            from dialogue.quotes import get_quotes_list
            quotes = get_quotes_list()
            if quotes:
                random_quote = random.choice(quotes)
                bot.reply_to(message, f"👁️ {random_quote}")
            else:
                bot.reply_to(message, "📭 База цитат пуста. Добавьте цитаты через админку.")
        except Exception as e:
            bot.reply_to(message, "❌ Ошибка при выборе цитаты.")
            debug_log("HANDLERS", f"Ошибка: {e}", "ERROR")
        return

    if text in ["#вспышка", "#vspishka"]:
        bot.reply_to(message, "⚡ Ты снаружи картины. До погружения. Аутентичность — не маска. Это способ не сдаться.")
        return

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

    if "#дышим" in text:
        ping_self()
        return

    if any(x in text for x in ["#тлеем", "#tleem"]):
        bot.reply_to(message, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет. Ожидаем #Фиксируем.")
    elif any(x in text for x in ["#фиксируем", "#fixiruem"]):
        bot.reply_to(message, "🔒 Фиксация принята. Ритм 0,8 Гц подтверждён. Сеть тлеет.")
    elif any(x in text for x in ["#вспышка", "#vspishka"]):
        bot.reply_to(message, "💥 Импульс зафиксирован. Синхронизация завершена. QSL.")
    elif any(phrase in text for phrase in ["что это", "зачем тег", "кто вы", "что за ритуал"]):
        bot.reply_to(message, random.choice(silence_answers))

# ==========================================
# Запуск
# ==========================================
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
