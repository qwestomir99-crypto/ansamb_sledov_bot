# ==========================================
# Файл: services/tg_api.py
# Справка: README.md → Telegram API
# Задача: отправка сообщений в Telegram
# Комментарий: защищён от байтов и кривых данных
# ==========================================

import requests
from debug_utils import debug_log
from services.secrets_manager import get_secret

# ==========================================
# ЗАЩИТНЫЕ ФУНКЦИИ
# ==========================================

def ensure_string(value, default=""):
    if value is None:
        return default
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin1')
    return str(value)

def ensure_int(value, default=0):
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# ==========================================
# ОСНОВНЫЕ ФУНКЦИИ
# ==========================================

def log_tg(level, message):
    debug_log("TG_API", message, level)

def get_bot_token():
    token = get_secret("BOT_TOKEN")
    return ensure_string(token)

def get_chat_id():
    chat_id = get_secret("TG_CHAT_ID", "@qwestomir")
    return ensure_string(chat_id)

def send_telegram_message(text, parse_mode='HTML'):
    """Отправляет сообщение в Telegram"""
    token = get_bot_token()
    chat_id = get_chat_id()
    
    if not token:
        log_tg("ERROR", "Нет токена бота")
        return False
    if not chat_id:
        log_tg("ERROR", "Нет chat_id")
        return False
    if not text:
        log_tg("WARNING", "Пустое сообщение")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            log_tg("INFO", f"Сообщение отправлено в {chat_id}")
            return True
        log_tg("ERROR", f"Ошибка TG: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        log_tg("ERROR", f"Ошибка отправки: {e}")
        return False

def send_telegram_photo(photo_url, caption=''):
    """Отправляет фото в Telegram"""
    token = get_bot_token()
    chat_id = get_chat_id()
    
    if not token:
        log_tg("ERROR", "Нет токена бота")
        return False
    if not chat_id:
        log_tg("ERROR", "Нет chat_id")
        return False
    if not photo_url:
        log_tg("ERROR", "Нет URL фото")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    data = {
        'chat_id': chat_id,
        'photo': photo_url,
        'caption': caption
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            log_tg("INFO", f"Фото отправлено в {chat_id}")
            return True
        log_tg("ERROR", f"Ошибка TG: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        log_tg("ERROR", f"Ошибка отправки: {e}")
        return False

if __name__ == "__main__":
    print("Telegram API модуль загружен")
