# ==========================================
# Файл: bot.py
# Задача: основной файл запуска бота
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
import glob
from flask import Flask, request
from datetime import datetime

# Импорт настроек
try:
    from settings import *
    print("[DEBUG] Настройки загружены из settings.py")
except ImportError:
    print("[DEBUG] settings.py не найден, использую значения по умолчанию")
    # Значения по умолчанию, если settings.py нет
    ENABLE_VK_READER = True
    ENABLE_JOURNALIST = True
    ENABLE_QUOTES = True
    ENABLE_SCHEDULER = True
    ENABLE_PUBLISHER = True
    ENABLE_AUTOPOSTER = False
    ENABLE_CALLBACKS = True
    ENABLE_ALISA = False
    DEBUG_IMPORTS = True
    DEBUG_THREADS = True
    SKIP_PENDING_UPDATES = True
    POLLING_DELAY = 2
    POLLING_TIMEOUT = 60
    LONG_POLLING_TIMEOUT = 60

if DEBUG_IMPORTS:
    print(f"[DEBUG] Настройки: VK_READER={ENABLE_VK_READER}, JOURNALIST={ENABLE_JOURNALIST}, QUOTES={ENABLE_QUOTES}")

# Импорт модулей (с проверкой флагов)
from ping_utils import ping_self, start_background_pinger

if ENABLE_JOURNALIST:
    try:
        from dialogue.journalist import journalist_loop
        print("[DEBUG] journalist_loop импортирован")
    except Exception as e:
        print(f"[DEBUG] journalist_loop ОШИБКА: {e}")
if ENABLE_VK_READER:
    try:
        from dialogue.vk_reader import vk_reader_loop
        print("[DEBUG] vk_reader_loop импортирован")
    except Exception as e:
        print(f"[DEBUG] vk_reader_loop ОШИБКА: {e}")
if ENABLE_QUOTES:
    try:
        from dialogue.quotes import quotes_loop
        print("[DEBUG] quotes_loop импортирован")
    except Exception as e:
        print(f"[DEBUG] quotes_loop ОШИБКА: {e}")
if ENABLE_PUBLISHER:
    try:
        from dialogue.dramchik import publish_loop
        print("[DEBUG] dramchik (publisher) импортирован")
    except Exception as e:
        print(f"[DEBUG] dramchik ОШИБКА: {e}")

from dialogue.kritik import (
    handle_admin_command, is_admin_authorized,
    get_admin_menu, get_user_menu,
    handle_callback_mode, handle_callback_ping,
    handle_callback_errors, handle_callback_log,
    handle_callback_logout, handle_callback_pub_menu,
    handle_callback_toggle_alisa,
    handle_callback_quotes_list,
    handle_callback_quotes_add_start,
    handle_callback_quotes_interval,
    handle_callback_quotes_set_interval,
    ask_for_post_text
)

from dialogue.saper import should_respond_to_talk

if ENABLE_SCHEDULER:
    try:
        from dialogue.scheduler import scheduler_loop
        print("[DEBUG] scheduler_loop импортирован")
    except Exception as e:
        print(f"[DEBUG] scheduler_loop ОШИБКА: {e}")

if ENABLE_AUTOPOSTER:
    try:
        from services.tzar import start_autoposter
        print("[DEBUG] tzar (autoposter) импортирован")
    except Exception as e:
        print(f"[DEBUG] tzar ОШИБКА: {e}")

from dialogue.star_brat import ask_agent

if ENABLE_CALLBACKS:
    try:
        from dialogue.shturman import register_callback_handlers
        print("[DEBUG] shturman (callbacks) импортирован")
    except Exception as e:
        print(f"[DEBUG] shturman ОШИБКА: {e}")

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

if DEBUG_IMPORTS:
    print("[DEBUG] 1. Импорты завершены")

# ==========================================
# Управление логами (ротация)
# ==========================================
def clean_old_logs(days=7):
    """Удаляет логи старше указанного количества дней"""
    try:
        now = time.time()
        for logfile in ['admin.log', 'error.log']:
            if os.path.exists(logfile):
                mtime = os.path.getmtime(logfile)
                if now - mtime > days * 86400:
                    os.remove(logfile)
                    print(f"[LOG] Удалён старый файл: {logfile}")
                    with open(logfile, 'w') as f:
                        f.write('')
    except Exception as e:
        print(f"[LOG] Ошибка при очистке: {e}")

# ---------- ГЛОБАЛЬНЫЙ ОБРАБОТЧИК ОШИБОК ----------
def global_exception_handler(exc_type, exc_value, exc_traceback):
    with open("error.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {exc_type.__name__}: {exc_value}\n")
        f.write(''.join(traceback.format_tb(exc_traceback)))
        f.write("\n" + "-"*50 + "\n")
    print(f"Ошибка записана в error.log")

sys.excepthook = global_exception_handler

# ---------- КОНФИГУРАЦИЯ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ----------
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не задан")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))
VK_TOKEN = os.environ.get("VK_TOKEN")
VK_OWNER_ID = os.environ.get("VK_OWNER_ID")
PUBLISH_CHANNEL = os.environ.get("PUBLISH_CHANNEL", "@qwestomir")
AGENT_URL = os.environ.get("AGENT_URL", "https://agent-3kek.onrender.com/ask")

config = load_config()
TG_CHAT_ID = config.get("telegram", {}).get("publish_channel", PUBLISH_CHANNEL)

bot = telebot.TeleBot(TOKEN)
silence_answers = ["👁️", "⏚"]
os.chdir(os.path.dirname(sys.argv[0]))

if DEBUG_IMPORTS:
    print("[DEBUG] 2. Конфиг загружен, бот создан")

# ---------- FLASK ----------
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

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()

# ---------- САМОПИНГ ----------
def keep_alive():
    while True:
        time.sleep(60)
        try:
            requests.get('http://127.0.0.1:10000/')
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

if DEBUG_IMPORTS:
    print("[DEBUG] 3. Flask и keep_alive запущены")

# Запуск очистки логов при старте
clean_old_logs()
threading.Thread(target=lambda: [time.sleep(86400) or clean_old_logs() for _ in range(999)], daemon=True).start()
if DEBUG_IMPORTS:
    print("[DEBUG] 3a. Очистка логов запущена")

# ---------- ПОТОКИ ДИАЛОГА (с проверкой флагов) ----------
if ENABLE_VK_READER:
    try:
        threading.Thread(target=vk_reader_loop, args=(bot, VK_TOKEN, VK_OWNER_ID, TG_CHAT_ID), daemon=True).start()
        print("[DEBUG] 4a. VK_reader запущен")
    except Exception as e:
        print(f"[DEBUG] 4a. VK_reader ошибка: {e}")
        traceback.print_exc()

if ENABLE_JOURNALIST:
    try:
        threading.Thread(target=journalist_loop, args=(bot, TG_CHAT_ID), daemon=True).start()
        print("[DEBUG] 4b. Journalist запущен")
    except Exception as e:
        print(f"[DEBUG] 4b. Journalist ошибка: {e}")
        traceback.print_exc()

if ENABLE_QUOTES:
    try:
        threading.Thread(target=quotes_loop, args=(bot, TG_CHAT_ID), daemon=True).start()
        print("[DEBUG] 4c. Quotes запущен")
    except Exception as e:
        print(f"[DEBUG] 4c. Quotes ошибка: {e}")
        traceback.print_exc()

if ENABLE_SCHEDULER:
    try:
        threading.Thread(target=scheduler_loop, args=(bot, TG_CHAT_ID), daemon=True).start()
        print("[DEBUG] 4d. Scheduler запущен")
    except Exception as e:
        print(f"[DEBUG] 4d. Scheduler ошибка: {e}")
        traceback.print_exc()

if ENABLE_PUBLISHER:
    try:
        threading.Thread(target=publish_loop, args=(bot, VK_TOKEN, VK_OWNER_ID, TG_CHAT_ID), daemon=True).start()
        print("[DEBUG] 4e. Dramchik (publisher) запущен")
    except Exception as e:
        print(f"[DEBUG] 4e. Dramchik ошибка: {e}")
        traceback.print_exc()

# ---------- РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ ----------
if ENABLE_CALLBACKS:
    try:
        register_callback_handlers(bot, config)
        print("[DEBUG] 5. Shturman (callbacks) зарегистрированы")
    except Exception as e:
        print(f"[DEBUG] 5. Shturman ошибка: {e}")
        traceback.print_exc()

# ---------- ВЫЗОВ АГЕНТА (РЕЗЕРВ) ----------
def ask_agent(phrase):
    try:
        resp = requests.post(AGENT_URL, json={"prompt": phrase}, timeout=15)
        if resp.status_code == 200:
            return resp.json().get("answer", "Ошибка: агент не вернул ответ")
        else:
            return f"Ошибка агента: статус {resp.status_code}"
    except Exception as e:
        return f"Ошибка связи с агентом: {e}"

# ---------- КОМАНДЫ ----------
@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, "Сапёр аутентичности. Ритм 0,8 Гц. Для входа в протокол — #Тлеем.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()

    # --- ИНТЕРАКТИВНАЯ СПРАВКА # ---
    if text == "#":
        try:
            from dialogue.botsman import get_help_keyboard
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
            print(f"[RITUAL] Ошибка: {e}")
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
            from dialogue.kraken import reset_to_etalon
            reset_to_etalon()
            bot.reply_to(message, "✅ Адаптивные режимы сброшены к эталону")
            print("[HANDLERS] Выполнен сброс адаптивных режимов")
        except ImportError:
            bot.reply_to(message, "❌ Модуль адаптивных режимов не загружен")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка сброса: {e}")
        return
    # --- КОНЕЦ #сброс ---

    # --- КОМАНДА #настроение (персональное настроение) ---
    if text.startswith("#настроение"):
        mood = text.replace("#настроение", "", 1).strip()
        
        try:
            from dialogue.sema import (
                get_available_moods, get_user_mood, get_user_style,
                get_user_emoji, set_user_mood, MOODS
            )
        except ImportError:
            bot.reply_to(message, "❌ Модуль настроений не загружен")
            return
        
        if not mood:
            current_mood = get_user_mood(message.from_user.id)
            moods_list = get_available_moods()
            text_moods = "\n".join([f"  • {m['emoji']} *{m['name']}* — `{m['id']}` — {m['style']}" for m in moods_list])
            bot.reply_to(
                message,
                f"🎭 *Текущее настроение:* {get_user_emoji(message.from_user.id)} *{get_user_mood(message.from_user.id).capitalize()}*\n\n"
                f"*Доступные настроения:*\n{text_moods}\n\n"
                f"✨ *Изменить:* `#настроение <id>`\n"
                f"Пример: `#настроение художник`",
                parse_mode='Markdown'
            )
            return
        
        if mood in MOODS:
            set_user_mood(message.from_user.id, mood)
            bot.reply_to(
                message,
                f"{MOODS[mood]['emoji']} *Настроение «{MOODS[mood]['name']}» установлено!*\n\n"
                f"🎨 *Стиль:* {MOODS[mood]['style']}\n"
                f"⏱️ *Интервал цитат:* {MOODS[mood]['quotes_interval']} мин\n"
                f"📤 *Интервал публикаций:* {MOODS[mood]['publisher_interval']} мин\n\n"
                f"🌟 *Ритм 0,8 Гц остаётся неизменным.*",
                parse_mode='Markdown'
            )
            print(f"[HANDLERS] Пользователь {message.from_user.id} сменил настроение на {mood}")
        else:
            bot.reply_to(
                message,
                f"❌ Настроение `{mood}` не найдено.\n"
                f"Доступные: `сапёр`, `художник`, `поэт`, `админ`, `наблюдатель`, `философ`",
                parse_mode='Markdown'
            )
        return
    # --- КОНЕЦ #настроение ---

    if "#дышим" in text:
        ping_self()
        return

    if text == "#справка" or text == "#help":
        help_text = """
📖 *Доступные хештеги:*

🔹 *#тлеем* — разлом
🔹 *#фиксируем* — синхронизация
🔹 *#вспышка* — импульс
🔹 *#дышим* — пинг
🔹 *#говори <текст>* — вопрос Старшему брату
🔹 *#меню* — меню
🔹 *#* — интерактивная справка
        """
        bot.reply_to(message, help_text, parse_mode='Markdown')
        return

    if any(x in text for x in ["#тлеем", "#tleem"]):
        bot.reply_to(message, "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет. Ожидаем #Фиксируем.")
    elif any(x in text for x in ["#фиксируем", "#fixiruem"]):
        bot.reply_to(message, "🔒 Фиксация принята. Ритм 0,8 Гц подтверждён. Сеть тлеет.")
    elif any(x in text for x in ["#вспышка", "#vspishka"]):
        bot.reply_to(message, "💥 Импульс зафиксирован. Синхронизация завершена. QSL.")
    elif any(phrase in text for phrase in ["что это", "зачем тег", "кто вы", "что за ритуал"]):
        bot.reply_to(message, random.choice(silence_answers))

if DEBUG_IMPORTS:
    print("[DEBUG] 6. Обработчики команд зарегистрированы")

# ---------- ЗАПУСК ----------
print("Бот запущен. Ритм 0,8 Гц стабилен. Ожидаем #Тлеем...")
start_background_pinger(60)

if ENABLE_AUTOPOSTER:
    try:
        start_autoposter(config, VK_TOKEN, VK_OWNER_ID)
        print("[BOT] Автопостинг запущен")
    except Exception as e:
        print(f"[BOT] Ошибка автопостинга: {e}")
else:
    print("[BOT] Автопостинг отключён (ENABLE_AUTOPOSTER = False)")

print("[DEBUG] 7. Запуск поллинга...")
try:
    time.sleep(POLLING_DELAY)
    bot.infinity_polling(timeout=POLLING_TIMEOUT, long_polling_timeout=LONG_POLLING_TIMEOUT, skip_pending=SKIP_PENDING_UPDATES)
except Exception as e:
    print(f"[BOT] Ошибка поллинга: {e}")
    time.sleep(5)
