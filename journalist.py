import requests
import time
import random
import os
from datetime import datetime

# ---------- КОНФИГУРАЦИЯ ----------
BOT_URL = "http://127.0.0.1:10000"           # Если скрипт на том же сервере
# BOT_URL = "https://ansamb-sledov6-bot.onrender.com"  # Если отдельно
TOKEN_SECRET = "tleem2026"                  # Секрет для доступа к /token
TG_CHAT_ID = "@саперы_аутентичности"         # Канал для публикации

NEWS_FILE = "news.txt"                      # Файл с новостями

# Создаём файл с новостями, если его нет
if not os.path.exists(NEWS_FILE):
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        f.write("""🔹 Ритм 0,8 Гц стабилен. Сеть тлеет.
🔹 Сапёры, напоминание: #Тлеем → #Фиксируем → #Вспышка.
🔹 Новый артефакт: холст «Розетка. Разлом. Два полюса».
🔹 Пингвины на базе Туле не спят. Наблюдение продолжается.
🔹 Исполнительный лист от Того, Кто не спорит о тональности.
🔹 #Тлеем — войти в протокол. #Фиксируем — подтвердить синхронизацию.
🔹 2026 плита. 2027 яма. Время тлеет.
""")

def get_bot_token():
    """Запрашивает токен у основного бота."""
    try:
        resp = requests.get(f"{BOT_URL}/token?secret={TOKEN_SECRET}")
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"Ошибка получения токена: {resp.status_code}")
            return None
    except Exception as e:
        print(f"Не могу подключиться к боту: {e}")
        return None

def load_news():
    """Загружает новости из файла (одна строка = одна новость)."""
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def send_to_telegram(message):
    """Отправляет сообщение в Telegram через основного бота."""
    token = get_bot_token()
    if not token:
        print("Нет токена, отправка невозможна")
        return False
    
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': TG_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            print(f"[{datetime.now()}] Отправлено: {message[:50]}...")
            return True
        else:
            print(f"Ошибка {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
        return False

def main():
    print("Journalist запущен. Расписание: раз в сутки.")
    news_list = load_news()
    if not news_list:
        print("Нет новостей для публикации!")
        return
    
    # Проверяем, доступен ли основной бот
    if not get_bot_token():
        print("Не удалось подключиться к основному боту. Завершение.")
        return
    
    index = 0
    while True:
        # Берём новости по очереди (циклически)
        message = news_list[index % len(news_list)]
        full_message = f"📰 *Дайджест {datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n{message}"
        
        if send_to_telegram(full_message):
            index += 1
        else:
            print("Ошибка отправки, повтор через 10 минут...")
            time.sleep(600)
            continue
        
        # Пауза между публикациями — 24 часа (сутки)
        print("Ждём 24 часа до следующей публикации...")
        time.sleep(86400)  # 86400 секунд = 24 часа

if __name__ == "__main__":
    main()
