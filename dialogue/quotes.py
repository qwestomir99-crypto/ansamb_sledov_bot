# ==========================================
# Модуль: dialogue/quotes.py
# Справка: README.md → Цитаты
# Задача: публикация цитат с YouTube-видео в TG и VK + шаббат
# Комментарий: VK — группа через VK_GROUP_ID
# ==========================================

import os
import time
import random
import json
import threading
from debug_utils import debug_log
from dialogue.activity_modes import should_publish_quotes
from services.sqlite_client import get_quotes, get_quotes_list, add_quote

# Путь к файлу конфигурации
CONFIG_FILE = os.path.join('dialogue', 'data', 'config.json')

def load_config():
    with open(CONFIG_FILE, "r", encoding='utf-8') as f:
        return json.load(f)

def set_quotes_interval(minutes):
    config = load_config()
    if "quotes" not in config:
        config["quotes"] = {}
    config["quotes"]["interval_minutes"] = minutes
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def get_quotes_interval():
    return load_config().get("quotes", {}).get("interval_minutes", 60)

def send_quote_with_photo(bot, chat_id, quote):
    try:
        from dialogue.youtube_auto import get_random_video
        video = get_random_video()
        caption = f"📜 {quote}\n\n🎬 {video['title']}\n{video['url']}" if video and video.get('url') else f"📜 {quote}"
        if len(caption) > 1024:
            caption = caption[:1024]
        bot.send_message(chat_id, caption)
        debug_log("QUOTES", "Цитата отправлена в Telegram")
        
        vk_token = os.getenv("VK_TOKEN")
        vk_group_id = os.getenv("VK_GROUP_ID")
        if vk_token and vk_group_id:
            try:
                from dialogue.publisher_utils import post_to_vk
                post_to_vk(caption, "#Цитата #СапёрыАутентичности", vk_token, vk_group_id)
                debug_log("QUOTES", "Цитата отправлена в VK")
            except Exception as e:
                debug_log("QUOTES", f"Ошибка VK: {e}", "WARNING")
        return True
    except Exception as e:
        debug_log("QUOTES", f"Ошибка: {e}", "ERROR")
        bot.send_message(chat_id, f"📜 {quote}\n\n#Цитата #СапёрыАутентичности")
        return False

quote_thread_running = False
quote_thread = None

def quotes_loop(bot, TG_CHAT_ID):
    global quote_thread_running, quote_thread
    quote_thread_running = False
    if quote_thread and quote_thread.is_alive():
        time.sleep(1)
    quote_thread_running = True
    
    def _run():
        last_interval = None
        while quote_thread_running:
            try:
                from dialogue.shabbat_manager import is_shabbat
                if is_shabbat():
                    time.sleep(3600)
                    continue
            except ImportError:
                pass
            if not should_publish_quotes():
                time.sleep(60)
                continue
            base_interval = get_quotes_interval()
            if base_interval != last_interval:
                last_interval = base_interval
            if base_interval <= 0:
                time.sleep(60)
                continue
            time.sleep(base_interval * 60)
            if not quote_thread_running or not should_publish_quotes():
                continue
            try:
                from dialogue.shabbat_manager import is_shabbat
                if is_shabbat():
                    continue
            except ImportError:
                pass
            quotes = get_quotes()
            if not quotes:
                continue
            send_quote_with_photo(bot, TG_CHAT_ID, random.choice(quotes))
    
    quote_thread = threading.Thread(target=_run, daemon=True)
    quote_thread.start()
    debug_log("QUOTES", "Цитаты запущены (TG + VK группа + шаббат)")
