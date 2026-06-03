# ==========================================
# Файл: dialogue/scheduler.py
# Справка: README.md → Планировщик / Полуночный ритуал
# Задача: отправка мантры в полночь, эволюция агента, перезагрузка бота
# Комментарий: проверяет время раз в минуту, выполняет ритуалы не чаще раза в день
# Зависит от: time, json, datetime, pytz, evolve_agent
# Вызывается из: bot.py (отдельный поток, если ENABLE_SCHEDULER = True)
# ==========================================

import time
import json
import os
import sys
from datetime import datetime
import pytz
from debug_utils import debug_log
from evolve_agent import evolve_agent, get_evolution_stats

CONFIG_FILE = "config.json"
RITUAL_TIMEZONE = pytz.timezone('Europe/Moscow')

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_last_ritual_date(date_str):
    config = load_config()
    if "ritual" not in config:
        config["ritual"] = {}
    config["ritual"]["last_midnight"] = date_str
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def load_last_ritual_date():
    config = load_config()
    return config.get("ritual", {}).get("last_midnight")

def log_scheduler(level, message):
    debug_log("SCHEDULER", message, level)

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
        log_scheduler("INFO", f"Полуночный ритуал отправлен в {tg_chat_id}")
    except Exception as e:
        log_scheduler("ERROR", f"Ошибка ритуала: {e}")

def perform_evolution_and_restart(bot, admin_id):
    """Выполняет эволюцию агента и перезагружает бота"""
    log_scheduler("INFO", "🔥 НАЧАЛО ЭВОЛЮЦИИ АГЕНТА 🔥")
    
    # 1. Эволюция
    rules_added = evolve_agent()
    stats = get_evolution_stats()
    log_scheduler("INFO", f"Эволюция завершена: добавлено {rules_added} правил. Всего правил: {stats['total_rules']}")
    
    # 2. Уведомление админу
    if admin_id and bot:
        try:
            bot.send_message(
                admin_id,
                f"🔥 *Полуночная эволюция завершена!*\n\n"
                f"📊 *Результаты:*\n"
                f"• Добавлено правил: {rules_added}\n"
                f"• Всего правил: {stats['total_rules']}\n"
                f"• Накоплено осадка: {stats['total_sediments']}\n\n"
                f"🔄 Бот перезагружается для применения обновлений...",
                parse_mode='Markdown'
            )
        except Exception as e:
            log_scheduler("ERROR", f"Не удалось отправить уведомление: {e}")
    
    # 3. Перезагрузка бота (Render перезапустит процесс)
    log_scheduler("INFO", "🔄 Перезагрузка бота...")
    time.sleep(2)  # Даём время на отправку сообщения
    sys.exit(0)  # Выход — Render автоматически перезапустит

def check_midnight_ritual(bot, tg_chat_id, admin_id):
    """
    Проверяет, нужно ли отправить ритуал и запустить эволюцию.
    Ориентируется на московское время.
    """
    now_moscow = datetime.now(RITUAL_TIMEZONE)
    
    # Полночь (00:00)
    if now_moscow.hour == 0 and now_moscow.minute == 0:
        today_str = now_moscow.strftime("%Y-%m-%d")
        last_ritual = load_last_ritual_date()
        if last_ritual != today_str:
            # 1. Отправляем мантру
            send_midnight_ritual(bot, tg_chat_id)
            # 2. Эволюция и перезагрузка
            perform_evolution_and_restart(bot, admin_id)
            save_last_ritual_date(today_str)

def scheduler_loop(bot, tg_chat_id, admin_id):
    """
    Основной поток планировщика.
    Проверяет различные задачи по расписанию.
    """
    log_scheduler("INFO", "Планировщик запущен")
    
    while True:
        try:
            check_midnight_ritual(bot, tg_chat_id, admin_id)
            # Здесь можно добавить другие задачи
        except Exception as e:
            log_scheduler("ERROR", f"Ошибка в цикле: {e}")
        
        time.sleep(60)  # Проверяем раз в минуту
