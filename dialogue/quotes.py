import time
import random
import os
from datetime import datetime

QUOTES_FILE = "quotes.txt"

def load_quotes():
    if not os.path.exists(QUOTES_FILE):
        # Создаём файл с примерами, если нет
        with open(QUOTES_FILE, "w", encoding="utf-8") as f:
            f.write("Ритм 0,8 Гц стабилен. Сеть тлеет.\n")
            f.write("Пингвины на базе Туле не спят.\n")
            f.write("Разлом. Два полюса. Ожидание.\n")
            f.write("Исполнительный лист от Того, Кто не спорит о тональности.\n")
            f.write("2026 плита. 2027 яма. Время тлеет.\n")
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def quotes_loop(bot, TG_CHAT_ID):
    quotes = load_quotes()
    if not quotes:
        return
    while True:
        # Публикуем раз в сутки в 9:00
        now = datetime.now()
        target = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= target:
            target = target.replace(day=now.day + 1)
        wait_seconds = (target - now).total_seconds()
        time.sleep(wait_seconds)

        quote = random.choice(quotes)
        message = f"📜 *Цитата дня* • {datetime.now().strftime('%d.%m.%Y')}\n\n{quote}\n\n#ЦитатаДня #СапёрыАутентичности"
        try:
            bot.send_message(TG_CHAT_ID, message, parse_mode='Markdown')
        except Exception as e:
            print(f"Цитата дня ошибка: {e}")
