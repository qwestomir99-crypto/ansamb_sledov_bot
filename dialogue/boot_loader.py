# ==========================================
# Файл: dialogue/boot_loader.py
# Справка: README.md → Загрузчик / Диспетчер запуска
# Задача: проверка состояния перед запуском бота и вебморды
# Комментарий: единая точка входа с защитой от 409
# Зависит от: requests, os, time
# Вызывается из: bot/main.py
# ==========================================

import os
import time
import requests
from debug_utils import debug_log

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = "https://ansamb-sledov-bot-94wz.onrender.com/webhook"
HEALTH_URL = "https://ansamb-sledov-bot-94wz.onrender.com/health"

def log_boot(level, message):
    debug_log("BOOT_LOADER", message, level)

def check_webhook():
    """Возвращает активный webhook (или None)"""
    try:
        r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
        data = r.json()
        if data.get("ok"):
            return data["result"].get("url")
    except Exception as e:
        log_boot("ERROR", f"Ошибка проверки webhook: {e}")
    return None

def delete_webhook():
    """Удаляет webhook"""
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        log_boot("INFO", "Webhook удалён")
        time.sleep(1)
    except Exception as e:
        log_boot("ERROR", f"Ошибка удаления webhook: {e}")

def set_webhook():
    """Устанавливает webhook для вебморды"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            data={"url": WEBHOOK_URL}
        )
        log_boot("INFO", f"Webhook установлен: {WEBHOOK_URL}")
    except Exception as e:
        log_boot("ERROR", f"Ошибка установки webhook: {e}")

def is_webmorda_alive():
    """Проверяет, отвечает ли вебморда"""
    try:
        r = requests.get(HEALTH_URL, timeout=5)
        return r.status_code == 200
    except:
        return False

def get_start_mode():
    """
    Определяет режим запуска:
    - "polling" — только бот (polling)
    - "webhook" — только вебморда (webhook)
    - "restart" — удалить webhook и запустить polling
    - "idle" — ничего не делать (всё работает)
    """
    webhook_url = check_webhook()
    webmorda_alive = is_webmorda_alive()
    
    log_boot("INFO", f"Webhook: {webhook_url}, Вебморда: {webmorda_alive}")
    
    if webhook_url and webmorda_alive:
        return "idle"
    elif webhook_url and not webmorda_alive:
        return "restart"
    elif not webhook_url and webmorda_alive:
        return "webhook"
    else:
        return "polling"

def wait_for_webmorda(bot=None, interval=60):
    """Ждёт, пока вебморда умрёт, чтобы запустить бота"""
    log_boot("INFO", "Ожидание состояния вебморды...")
    while True:
        time.sleep(interval)
        if not is_webmorda_alive():
            log_boot("INFO", "Вебморда недоступна, запускаем polling")
            break
        if bot:
            try:
                bot.send_message(
                    os.environ.get("ADMIN_USER_ID", 0),
                    "🔄 Вебморда жива, бот в режиме ожидания..."
                )
            except:
                pass
