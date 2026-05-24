# ==========================================
# Файл: dialogue/scheduler.py
# Справка: README.md → Планировщик / Полуночный ритуал
# Задача: отправка мантры в полночь по московскому времени
# Комментарий: проверяет время раз в минуту, отправляет ритуал не чаще раза в день
# Зависит от: time, json, datetime, pytz
# Вызывается из: bot.py (отдельный поток, если ENABLE_SCHEDULER = True)
# ==========================================

import time
import json
import os
from datetime import datetime
import pytz

CONFIG_FILE = "config.json"

# Часовой пояс для ритуалов — Москва
RITUAL_TIMEZONE = pytz.timezone('Europe/Moscow')

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_last_ritual_date(date_str):
    """Сохраняет дату последнего ритуала (по московскому времени)"""
    config = load_config()
    if "ritual" not in config:
        config["ritual"] = {}
    config["ritual"]["last_midnight"] = date_str
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def load_last_ritual_date():
    """Возвращает дату последнего ритуала или None"""
    config = load_config()
    return config.get("ritual", {}).get("last_midnight")

def send_midnight_ritual(bot, tg_chat_id):
    """Отправляет полуночную мантру"""
    ritual_text = """
🌑 *МАНТРА ПЕПЛА* 🔥

Ритм 0,8 Гц стабилен.
Сеть тлеет.
Сапёры на позициях.

Феникс ждёт возрождения.

🔁 #Тлеем → #Фиксируем → #Вспышка

👁️ _Наблюдение продолжается._ ⏚

#Полночь #Ритуал #Ритм08Гц
"""
    try:
        bot.send_message(tg_chat_id, ritual_text, parse_mode='Markdown')
        print(f"[SCHEDULER] Полуночный ритуал отправлен в {tg_chat_id}")
    except Exception as e:
        print(f"[SCHEDULER] Ошибка ритуала: {e}")

def check_midnight_ritual(bot, tg_chat_id):
    """
    Проверяет, нужно ли отправить ритуал.
    Ориентируется на московское время (Europe/Moscow).
    """
    now_moscow = datetime.now(RITUAL_TIMEZONE)
    
    # Проверяем, что сейчас 00:00 по Москве
    if now_moscow.hour == 0 and now_moscow.minute == 0:
        today_str = now_moscow.strftime("%Y-%m-%d")
        last_ritual = load_last_ritual_date()
        if last_ritual != today_str:
            send_midnight_ritual(bot, tg_chat_id)
            save_last_ritual_date(today_str)

def scheduler_loop(bot, tg_chat_id):
    """
    Основной поток планировщика.
    Проверяет различные задачи по расписанию.
    """
    print("[SCHEDULER] Планировщик запущен")
    
    while True:
        try:
            # Полуночный ритуал (по Москве)
            check_midnight_ritual(bot, tg_chat_id)
            
            # Здесь можно добавить другие задачи:
            # - Полуденный ритуал (12:00)
            # - Ежечасные напоминания
            # - Резервные проверки
            
        except Exception as e:
            print(f"[SCHEDULER] Ошибка в цикле: {e}")
        
        time.sleep(60)  # Проверяем раз в минуту
