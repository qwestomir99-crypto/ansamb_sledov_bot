# ==========================================
# Модуль: dialogue/quotes.py
# Справка: README.md → Цитаты
# Задача: публикация цитат по расписанию + случайный пост из VK
# Комментарий: интервал цитат зависит от настроения пользователя (если задано)
#              Исправлена логика: текст поста — приоритет №1, цитата — опциональна.
#              Поддержка Supabase с фоллбэком на файлы.
# Зависит от: config.json, activity_modes.py, user_settings.py, services.photo_reader, services.supabase_client
# Вызывается из: bot.py
# ==========================================

import time
import random
import os
import json
from datetime import datetime
import threading
from debug_utils import debug_log
from dialogue.activity_modes import should_publish_quotes, get_quotes_interval, load_config
from dialogue.user_settings import get_user_quotes_interval
from services.supabase_client import db_insert, db_select

CONFIG_FILE = "config.json"
QUOTES_TABLE = "quotes"
QUOTES_FALLBACK_FILE = "dialogue/data/quotes.txt"

# ==========================================
# РАБОТА С ЦИТАТАМИ
# ==========================================
def get_quotes(limit=10):
    """
    Возвращает список цитат.
    Сначала пытается взять из Supabase, при ошибке — из файла.
    """
    # Попытка из базы
    result = db_select(QUOTES_TABLE, limit=limit, fallback_file=None)
    if result:
        return [row.get("text") for row in result]
    
    # Фоллбэк на файл
    if os.path.exists(QUOTES_FALLBACK_FILE):
        with open(QUOTES_FALLBACK_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()][-limit:]
    return []

def add_quote(text):
    """
    Добавляет цитату.
    Сначала пытается записать в Supabase, при ошибке — в файл.
    """
    data = {"text": text, "created_at": datetime.now().isoformat()}
    db_insert(QUOTES_TABLE, data, fallback_file=QUOTES_FALLBACK_FILE)
    return True

# ==========================================
# ОСТАЛЬНОЙ КОД БЕЗ ИЗМЕНЕНИЙ
# ==========================================
def save_quotes(quotes):
    config = load_config()
    quotes_file = config.get("quotes", {}).get("file", QUOTES_FALLBACK_FILE)
    with open(quotes_file, "w", encoding="utf-8") as f:
        for q in quotes:
            f.write(q + "\n")

def delete_quote(index):
    quotes = get_quotes()
    if 0 <= index < len(quotes):
        quotes.pop(index)
        save_quotes(quotes)
        return True
    return False

def get_quotes_list():
    return get_quotes()

def get_quotes_interval_minutes():
    config = load_config()
    return config.get("quotes", {}).get("interval_minutes", 60)

def set_quotes_interval_minutes(minutes):
    config = load_config()
    if "quotes" not in config:
        config["quotes"] = {}
    config["quotes"]["interval_minutes"] = minutes
    save_config(config)

# ==========================================
# Глобальная переменная для остановки старого цикла
# ==========================================
quote_thread_running = False
quote_thread = None

def send_quote_with_photo(bot, chat_id, quote):
    """Отправляет цитату с фото из VK (приоритет — текст поста)"""
    try:
        from services.photo_reader import get_random_post
        
        post = get_random_post()
        if post and post.get('photo_url'):
            # Текст поста — главный
            caption = post['text']
            
            # Добавляем цитату, если влезает
            if len(caption) + len(quote) + 50 < 1024:
                caption += f"\n\n📜 {quote}"
            
            # Добавляем хештеги, если влезают
            tags = ' '.join(post.get('tags', [])[:3])
            if len(caption) + len(tags) + 10 < 1024:
                caption += f"\n\n{tags}"
            
            # Обрезаем до лимита Telegram на всякий случай
            caption = caption[:1024]
            
            bot.send_photo(chat_id, post['photo_url'], caption=caption, parse_mode='Markdown')
            debug_log("QUOTES", f"Цитата отправлена с фото (приоритет — текст поста, длина: {len(caption)} симв.)")
            return True
        else:
            bot.send_message(chat_id, f"📜 *Цитата дня* • {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n{quote}\n\n#ЦитатаДня #СапёрыАутентичности", parse_mode='Markdown')
            debug_log("QUOTES", "Цитата отправлена без фото (пост не найден)")
            return False
    except Exception as e:
        debug_log("QUOTES", f"Ошибка отправки цитаты с фото: {e}", "ERROR")
        # Если фото не отправилось — отправляем просто текст
        bot.send_message(chat_id, f"📜 *Цитата дня* • {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n{quote}\n\n#ЦитатаДня #СапёрыАутентичности", parse_mode='Markdown')
        return False

def quotes_loop(bot, TG_CHAT_ID):
    global quote_thread_running, quote_thread
    
    quote_thread_running = False
    if quote_thread and quote_thread.is_alive():
        time.sleep(1)
    
    quote_thread_running = True
    
    def _run():
        last_interval = None
        
        while quote_thread_running:
            if not should_publish_quotes():
                time.sleep(60)
                continue
            
            # Получаем базовый интервал из режима
            base_interval = get_quotes_interval()
            
            # Для общего канала используем базовый интервал (без привязки к пользователю)
            current_interval = base_interval
            
            if current_interval != last_interval:
                last_interval = current_interval
                debug_log("QUOTES", f"Интервал обновлён: {current_interval} минут")
            
            if current_interval <= 0:
                time.sleep(60)
                continue
            
            interval_seconds = current_interval * 60
            time.sleep(interval_seconds)
            
            if not quote_thread_running or not should_publish_quotes():
                continue
                
            quotes = get_quotes()
            if not quotes:
                continue
                
            quote = random.choice(quotes)
            
            # Отправляем цитату с фото из VK
            send_quote_with_photo(bot, TG_CHAT_ID, quote)
            debug_log("QUOTES", f"Цитата отправлена (интервал {current_interval} мин)")
    
    quote_thread = threading.Thread(target=_run, daemon=True)
    quote_thread.start()
    debug_log("QUOTES", "Цитаты запущены")

if __name__ == "__main__":
    print("📜 Цитаты — приоритет текста поста.")
    print("Запусти через bot.py, а не напрямую.")
