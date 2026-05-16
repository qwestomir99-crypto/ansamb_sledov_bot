import time
import random
import os
import json
from datetime import datetime

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_quotes():
    config = load_config()
    quotes_file = config.get("quotes", {}).get("file", "dialogue/data/quotes.txt")
    
    if not os.path.exists(quotes_file):
        os.makedirs(os.path.dirname(quotes_file), exist_ok=True)
        with open(quotes_file, "w", encoding="utf-8") as f:
            f.write("Ритм 0,8 Гц стабилен. Сеть тлеет.\n")
            f.write("Пингвины на базе Туле не спят.\n")
            f.write("Разлом. Два полюса. Ожидание.\n")
    
    with open(quotes_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def quotes_loop(bot, TG_CHAT_ID):
    quotes = load_quotes()
    if not quotes:
        return
    
    config = load_config()
    interval_hours = config.get("quotes", {}).get("interval_hours", 1)
    interval_seconds = interval_hours * 3600
    
    while True:
        time.sleep(interval_seconds)
        quote = random.choice(quotes)
        message = f"📜 *Цитата дня* • {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n{quote}\n\n#ЦитатаДня #СапёрыАутентичности"
        try:
            bot.send_message(TG_CHAT_ID, message, parse_mode='Markdown')
        except Exception as e:
            print(f"Цитата дня ошибка: {e}")
