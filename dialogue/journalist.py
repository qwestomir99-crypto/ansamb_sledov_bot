import time
import os
import json
from datetime import datetime

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_news():
    config = load_config()
    news_file = config.get("journalist", {}).get("news_file", "news.txt")
    
    if not os.path.exists(news_file):
        with open(news_file, "w", encoding="utf-8") as f:
            f.write("🔹 Ритм 0,8 Гц стабилен. Сеть тлеет.\n")
            f.write("🔹 #Тлеем → #Фиксируем → #Вспышка.\n")
    with open(news_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def journalist_loop(bot, TG_CHAT_ID):
    news_list = load_news()
    if not news_list:
        return
    
    config = load_config()
    interval_hours = config.get("journalist", {}).get("interval_hours", 24)
    interval_seconds = interval_hours * 3600
    
    index = 0
    while True:
        message = news_list[index % len(news_list)]
        full_message = f"📰 *Дайджест {datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n{message}"
        try:
            bot.send_message(TG_CHAT_ID, full_message, parse_mode='Markdown')
            index += 1
        except Exception as e:
            print(f"Журналист ошибка: {e}")
        time.sleep(interval_seconds)
