import time
from datetime import datetime
import os

def load_news():
    news_file = "news.txt"
    if not os.path.exists(news_file):
        return []
    with open(news_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def journalist_loop(bot, TG_CHAT_ID):
    news_list = load_news()
    if not news_list:
        print("Журналист: нет новостей")
        return
    index = 0
    while True:
        message = news_list[index % len(news_list)]
        full_message = f"📰 *Дайджест {datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n{message}"
        try:
            bot.send_message(TG_CHAT_ID, full_message, parse_mode='Markdown')
            index += 1
        except Exception as e:
            print(f"Журналист ошибка: {e}")
        time.sleep(86400)  # 24 часа
