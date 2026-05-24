# ==========================================
# Файл: bot.py
# Задача: единый процесс — Telegram-бот + веб-морда (Flask)
# Комментарий: запускается как web service на Render.
#              Веб-морда слушает порт, бот работает в фоновом потоке.
# ==========================================

print("[DEBUG] 0. Начало загрузки bot.py")

import telebot
import random
import os
import sys
import threading
import time
import requests
import json
from datetime import datetime
from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
from functools import wraps

# ==========================================
# НАСТРОЙКИ БОТА (из settings.py)
# ==========================================
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

if DEBUG_IMPORTS:
    print(f"[DEBUG] Настройки: VK_READER={ENABLE_VK_READER}, JOURNALIST={ENABLE_JOURNALIST}")

# Импорт модулей бота
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

# Конфиг и токены
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
# FLASK (ВЕБ-МОРДА)
# ==========================================
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "secret_traces_key_6")

# Внутреннее состояние для веб-морды
web_state = {
    "mode": "день",
    "quotes": [
        "Ритм задает движение, следы оставляют историю.",
        "Тестовая цитата ансамбля №6."
    ]
}

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session.clear()
            session['authenticated'] = True
            session.permanent = True
            return redirect(url_for('index'))
        else:
            error = 'Неверный пароль'
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Вход — Ансамбль Следов 6</title>
        <style>
            body {
                background: #0a0a0a;
                color: #00ffcc;
                font-family: 'Courier New', monospace;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .login-card {
                background: #111;
                border-left: 3px solid #00ffcc;
                padding: 2rem;
                border-radius: 8px;
                width: 300px;
            }
            input {
                background: #222;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                padding: 8px;
                width: 100%;
                margin: 10px 0;
                border-radius: 4px;
                font-family: inherit;
            }
            button {
                background: #222;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                padding: 8px;
                width: 100%;
                cursor: pointer;
                border-radius: 4px;
                font-family: inherit;
            }
            button:hover { background: #00ffcc; color: #000; }
            .error { color: #f00; margin-bottom: 10px; }
            h2 { margin-top: 0; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2>🔐 Вход в систему</h2>
            <form method="post">
                <input type="password" name="password" placeholder="Админ-пароль" autofocus>
                <button type="submit">Войти</button>
                <div class="error">''' + (error if error else '') + '''</div>
            </form>
        </div>
    </body>
    </html>
    '''

@flask_app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@flask_app.route('/')
@login_required
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ансамбль Следов 6 — веб-морда</title>
        <style>
            body { background: #0a0a0a; color: #00ffcc; font-family: monospace; padding: 2rem; }
            .card { background: #111; border-left: 3px solid #00ffcc; padding: 1rem; margin: 1rem 0; }
            button, input, textarea { background: #222; color: #00ffcc; border: 1px solid #00ffcc; padding: 6px 12px; }
            button:hover { background: #00ffcc; color: #000; cursor: pointer; }
            a { color: #00ffcc; }
        </style>
    </head>
    <body>
        <h1>🔥 Ансамбль Следов 6</h1>
        <p>Режим: <strong id="mode">{{ mode }}</strong></p>
        <p><a href="/logs/admin">📋 admin.log</a> | <a href="/logs/error">❌ error.log</a></p>
        
        <div class="card">
            <h2>🎬 Пост в VK</h2>
            <textarea id="post-text" rows="3" cols="50" placeholder="Текст поста..."></textarea><br>
            <button onclick="sendPost()">Отправить</button>
            <span id="status"></span>
        </div>
        
        <script>
        async function sendPost() {
            const text = document.getElementById('post-text').value;
            if (!text.trim()) return;
            const status = document.getElementById('status');
            status.innerText = '⏳ Отправка...';
            const resp = await fetch('/vk_post', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'text=' + encodeURIComponent(text)
            });
            const data = await resp.json();
            if (data.status === 'ok') {
                status.innerHTML = `✅ Опубликовано! <a href="${data.url}" target="_blank">Ссылка</a>`;
                document.getElementById('post-text').value = '';
            } else {
                status.innerText = '❌ ' + data.error;
            }
        }
        </script>
    </body>
    </html>
    ''', mode=web_state['mode'])

@flask_app.route('/ping')
def ping():
    return {"status": "ok", "service": "bot+web"}, 200

@flask_app.route('/vk_post', methods=['POST'])
@login_required
def vk_post():
    text = request.form.get('text', '').strip()
    if not text:
        return jsonify({"status": "error", "error": "Текст пуст"}), 400
    if not VK_TOKEN or not VK_OWNER_ID:
        return jsonify({"status": "error", "error": "VK_TOKEN не задан"}), 500
    try:
        import vk_api
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        owner_id = int(VK_OWNER_ID)
        post = vk.wall.post(owner_id=owner_id, message=text, from_group=1)
        post_id = post.get('post_id')
        post_url = f"https://vk.com/wall{owner_id}_{post_id}"
        return jsonify({"status": "ok", "url": post_url}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@flask_app.route('/logs/<name>')
@login_required
def view_log(name):
    log_file = f"{name}.log"
    if not os.path.exists(log_file):
        return f"Лог не найден", 404
    with open(log_file, 'r') as f:
        return f"<pre>{f.read()}</pre>"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False)

# ==========================================
# ЗАПУСК ПОТОКОВ БОТА
# ==========================================
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
# ЗАПУСК FLASK (в основном потоке)
# ==========================================
threading.Thread(target=run_flask, daemon=True).start()
print("[BOT] Flask-сервер (веб-морда) запущен в фоне")

# ==========================================
# ОБРАБОТЧИКИ КОМАНД TELEGRAM
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

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()
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
# ЗАПУСК БОТА
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
