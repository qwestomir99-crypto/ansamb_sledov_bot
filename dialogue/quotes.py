# ==========================================
# Модуль: dialogue/quotes.py
# Справка: README.md → Цитаты
# Задача: публикация цитат по расписанию
# Комментарий: интервал цитат зависит от настроения пользователя (если задано)
# Зависит от: config.json, activity_modes.py, user_settings.py
# Вызывается из: bot.py
# ==========================================

import time
import random
import os
import json
from datetime import datetime
import threading
from dialogue.activity_modes import should_publish_quotes, get_quotes_interval, load_config
from dialogue.user_settings import get_user_quotes_interval

CONFIG_FILE = "config.json"

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def load_quotes():
    config = load_config()
    quotes_file = config.get("quotes", {}).get("file", "dialogue/data/quotes.txt")
    
    if not os.path.exists(quotes_file):
        os.makedirs(os.path.dirname(quotes_file), exist_ok=True)
        default_quotes = [
            "💥 Разлом. Ритм 0,8 Гц. Сеть тлеет.",
            "🐧 Пингвины на базе Туле не спят. Наблюдение продолжается.",
            "🔒 Фиксация принята. Ритм 0,8 Гц подтверждён.",
            "📜 Нас нет, но мы дышим. Он есть, и мы помним.",
            "🎨 Розетка. Разлом. Два полюса. Союз не в целостности, а в разрыве.",
            "⏳ 2026 плита. Готовность 0,8 Гц.",
            "🛡 Сапёр аутентичности всегда на посту.",
            "🕯 Исполнительный лист от Того, Кто не спорит о тональности.",
            "🌊 Их рты полны воды. Мои холсты — правда.",
            "🔁 #Тлеем → #Фиксируем → #Вспышка. Цикл замкнут.",
            "👁 Сапёр аутентичности не объясняет. Он отвечает 👁 или ⏚.",
            "🐧 След на контакте. QSL.",
            "🔥 Михоель Ав ведёт.",
            "⏚ Тишина в эфире — знак качества.",
            "🌙 Сапёр не спит. Сапёр ждёт."
        ]
        with open(quotes_file, "w", encoding="utf-8") as f:
            for q in default_quotes:
                f.write(q + "\n")
    
    with open(quotes_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_quotes(quotes):
    config = load_config()
    quotes_file = config.get("quotes", {}).get("file", "dialogue/data/quotes.txt")
    with open(quotes_file, "w", encoding="utf-8") as f:
        for q in quotes:
            f.write(q + "\n")

def add_quote(text):
    quotes = load_quotes()
    quotes.append(text)
    save_quotes(quotes)

def delete_quote(index):
    quotes = load_quotes()
    if 0 <= index < len(quotes):
        quotes.pop(index)
        save_quotes(quotes)
        return True
    return False

def get_quotes_list():
    return load_quotes()

def get_quotes_interval_minutes():
    config = load_config()
    return config.get("quotes", {}).get("interval_minutes", 60)

def set_quotes_interval_minutes(minutes):
    config = load_config()
    if "quotes" not in config:
        config["quotes"] = {}
    config["quotes"]["interval_minutes"] = minutes
    save_config(config)

# Глобальная переменная для остановки старого цикла
quote_thread_running = False
quote_thread = None

def quotes_loop(bot, TG_CHAT_ID):
    global quote_thread_running, quote_thread
    
    quote_thread_running = False
    if quote_thread and quote_thread.is_alive():
        time.sleep(1)
    
    quote_thread_running = True
    
    def _run():
        last_interval = None
        
        while quote_thread_running:
            if not should_publish_quotes():
                time.sleep(60)
                continue
            
            # Получаем базовый интервал из режима
            base_interval = get_quotes_interval()
            
            # Для общего канала используем базовый интервал (без привязки к пользователю)
            # Но для отладки можно залогировать
            current_interval = base_interval
            
            if current_interval != last_interval:
                last_interval = current_interval
                print(f"[QUOTES] Интервал обновлён: {current_interval} минут")
            
            if current_interval <= 0:
                time.sleep(60)
                continue
            
            interval_seconds = current_interval * 60
            time.sleep(interval_seconds)
            
            if not quote_thread_running or not should_publish_quotes():
                continue
                
            quotes = load_quotes()
            if not quotes:
                continue
                
            quote = random.choice(quotes)
            message = f"📜 *Цитата дня* • {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n{quote}\n\n#ЦитатаДня #СапёрыАутентичности"
            try:
                bot.send_message(TG_CHAT_ID, message, parse_mode='Markdown')
                print(f"[QUOTES] Цитата отправлена (интервал {current_interval} мин)")
            except Exception as e:
                print(f"[QUOTES] Ошибка отправки: {e}")
    
    quote_thread = threading.Thread(target=_run, daemon=True)
    quote_thread.start()
    print(f"[QUOTES] Цитаты запущены")
