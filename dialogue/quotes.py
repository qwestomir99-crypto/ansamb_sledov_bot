import time
import random
import os
import json
from datetime import datetime
import threading

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def load_quotes():
    config = load_config()
    quotes_file = config.get("quotes", {}).get("file", "dialogue/data/quotes.txt")
    
    if not os.path.exists(quotes_file):
        os.makedirs(os.path.dirname(quotes_file), exist_ok=True)
        # Сапёрские цитаты по умолчанию
        default_quotes = [
            "Ритм 0,8 Гц стабилен. Сеть тлеет.",
            "Пингвины на базе Туле не спят.",
            "Разлом. Два полюса. Ожидание.",
            "Сапёр аутентичности всегда на посту.",
            "Тлеем. Фиксируем. Вспышка.",
            "След на контакте. QSL.",
            "Михоель Ав ведёт.",
            "2026 плита. Готовность 0,8 Гц."
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
    
    # Останавливаем старый цикл, если был
    quote_thread_running = False
    if quote_thread and quote_thread.is_alive():
        time.sleep(1)
    
    quote_thread_running = True
    
    def _run():
        while quote_thread_running:
            quotes = load_quotes()
            if not quotes:
                time.sleep(60)
                continue
            
            interval_minutes = get_quotes_interval_minutes()
            interval_seconds = interval_minutes * 60
            
            time.sleep(interval_seconds)
            
            if not quote_thread_running:
                break
                
            quote = random.choice(quotes)
            message = f"📜 *Цитата дня* • {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n{quote}\n\n#ЦитатаДня #СапёрыАутентичности"
            try:
                bot.send_message(TG_CHAT_ID, message, parse_mode='Markdown')
            except Exception as e:
                print(f"[QUOTES] Ошибка отправки: {e}")
    
    quote_thread = threading.Thread(target=_run, daemon=True)
    quote_thread.start()
    print(f"[QUOTES] Цитаты запущены, интервал {get_quotes_interval_minutes()} минут")
