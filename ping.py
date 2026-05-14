import requests
import time
import os

# Твой основной бот на Render
URL = "https://ansamb-sledov-bot-94wz.onrender.com/"

def main():
    print("Сервис-будильник запущен. Пингую бота каждые 4 минуты...")
    while True:
        try:
            r = requests.get(URL, timeout=30)
            print(f"Пинг отправлен. Статус: {r.status_code}")
        except Exception as e:
            print(f"Ошибка пинга: {e}")
        time.sleep(240)  # 240 секунд = 4 минуты (запас до 15 минут сна)

if __name__ == "__main__":
    main()
