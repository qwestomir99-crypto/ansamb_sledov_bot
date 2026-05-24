# ==========================================
# Файл: dialogue/publisher.py
# Справка: README.md → Публикатор
# Задача: публикация отложенных постов и постов из пула (post_pool.json)
# Комментарий: поддерживает Telegram и VK, добавляет отчёты и автоудаление
# Зависит от: activity_modes.py, publisher_utils.py, post_manager.py
# Вызывается из: bot.py (отдельный поток)
# ==========================================

import time
import json
import os
import random
import threading
from datetime import datetime
from debug_utils import debug_log
from dialogue.activity_modes import should_publish, get_current_mode_config
from dialogue.publisher_utils import post_to_telegram, post_to_vk, get_random_own_post_from_vk
from dialogue.post_manager import get_post_for_publishing, build_tags

PUBLICATIONS_FILE = "publications.json"
CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_publications():
    if not os.path.exists(PUBLICATIONS_FILE):
        return []
    with open(PUBLICATIONS_FILE, "r") as f:
        return json.load(f)

def save_publications(pubs):
    with open(PUBLICATIONS_FILE, "w") as f:
        json.dump(pubs, f, indent=2)

def add_publication(platform, text, delay_seconds, tags, file_path=None):
    pubs = load_publications()
    publish_at = time.time() + delay_seconds
    pubs.append({
        "platform": platform,
        "text": text,
        "publish_at": publish_at,
        "tags": tags,
        "file_path": file_path,
        "status": "pending"
    })
    save_publications(pubs)

def publish_post(bot, tg_chat_id, vk_token, vk_owner_id, post, platform="both"):
    text = post.get("text", "")
    tags = build_tags(post)
    full_message = f"{text}\n\n{tags}" if text else tags
    
    success_tg = False
    success_vk = False
    
    if platform in ["both", "telegram"]:
        try:
            success_tg = post_to_telegram(bot, tg_chat_id, text, None, tags)
            debug_log("PUBLISHER", f"Telegram: {'✅' if success_tg else '❌'}")
        except Exception as e:
            debug_log("PUBLISHER", f"Telegram ошибка: {e}", "ERROR")
    
    if platform in ["both", "vk"] and vk_token and vk_owner_id:
        try:
            config = load_config()
            repost_enabled = config.get("settings", {}).get("REPOST_ENABLED", False)
            
            if repost_enabled and random.randint(1, 100) <= config.get("settings", {}).get("REPOST_QUOTE_CHANCE", 50):
                repost_from = get_random_own_post_from_vk()
                if repost_from:
                    debug_log("PUBLISHER", f"Репост из VK поста {repost_from.get('post_id')}")
                    success_vk, error = post_to_vk(
                        text, tags, vk_token, vk_owner_id, None,
                        auto_quote=True, auto_tags=True, repost_from=repost_from
                    )
                else:
                    success_vk, error = post_to_vk(text, tags, vk_token, vk_owner_id, None)
            else:
                success_vk, error = post_to_vk(text, tags, vk_token, vk_owner_id, None)
            
            debug_log("PUBLISHER", f"VK: {'✅' if success_vk else '❌'}")
        except Exception as e:
            debug_log("PUBLISHER", f"VK ошибка: {e}", "ERROR")
    
    return success_tg or success_vk

def safe_delete(bot, chat_id, message, delay=3):
    """Безопасное удаление сообщения с задержкой"""
    def _delete():
        time.sleep(delay)
        try:
            bot.delete_message(chat_id, message.message_id)
        except:
            pass
    threading.Thread(target=_delete, daemon=True).start()

def send_report(bot, chat_id, text, delete_after=5):
    """Отправляет отчёт и удаляет его через delete_after секунд"""
    msg = bot.send_message(chat_id, text)
    if delete_after > 0:
        safe_delete(bot, chat_id, msg, delete_after)

def publish_loop(bot, vk_token, vk_owner_id, tg_chat_id):
    """Основной цикл публикатора с отчётами"""
    debug_log("PUBLISHER", "Поток публикатора запущен, проверка каждые 30 секунд")
    
    last_pool_check = 0
    last_interval = None
    
    while True:
        try:
            mode_config = get_current_mode_config()
            pool_interval = mode_config.get("publisher_interval", 0)
            
            if pool_interval != last_interval:
                last_interval = pool_interval
                if pool_interval > 0:
                    debug_log("PUBLISHER", f"Интервал публикаций обновлён: {pool_interval} минут")
                else:
                    debug_log("PUBLISHER", "Публикации отключены в текущем режиме")
            
            if not should_publish() or pool_interval <= 0:
                time.sleep(30)
                continue
            
            # Отложенные публикации
            pubs = load_publications()
            now = time.time()
            changed = False
            
            for pub in pubs[:]:
                if pub.get("status") != "pending":
                    continue
                
                if pub["publish_at"] <= now:
                    platform = pub["platform"]
                    text = pub.get("text")
                    tags = pub.get("tags", "")
                    file_path = pub.get("file_path")
                    
                    success = False
                    error_msg = None
                    
                    if platform == "telegram":
                        try:
                            success = post_to_telegram(bot, tg_chat_id, text, file_path, tags)
                            if not success:
                                error_msg = "Ошибка отправки в Telegram"
                        except Exception as e:
                            error_msg = str(e)
                    elif platform == "vk":
                        try:
                            config = load_config()
                            repost_enabled = config.get("settings", {}).get("REPOST_ENABLED", False)
                            
                            if repost_enabled and random.randint(1, 100) <= config.get("settings", {}).get("REPOST_QUOTE_CHANCE", 50):
                                repost_from = get_random_own_post_from_vk()
                                if repost_from:
                                    success, error_msg = post_to_vk(
                                        text, tags, vk_token, vk_owner_id, file_path,
                                        auto_quote=True, auto_tags=True, repost_from=repost_from
                                    )
                                else:
                                    success, error_msg = post_to_vk(text, tags, vk_token, vk_owner_id, file_path)
                            else:
                                success, error_msg = post_to_vk(text, tags, vk_token, vk_owner_id, file_path)
                        except Exception as e:
                            error_msg = str(e)
                    
                    if success:
                        pub["status"] = "published"
                        pub["published_at"] = now
                        changed = True
                        send_report(bot, tg_chat_id, f"✅ Пост опубликован в {platform.upper()}!")
                    else:
                        send_report(bot, tg_chat_id, f"❌ Ошибка публикации в {platform.upper()}: {error_msg}")
                    
                    time.sleep(1)
            
            if changed:
                save_publications(pubs)
            
            # Очистка старых публикаций
            cleaned = False
            new_pubs = []
            for pub in pubs:
                if pub["status"] == "published":
                    if pub.get("published_at", 0) < now - 86400:
                        cleaned = True
                        continue
                new_pubs.append(pub)
            
            if cleaned:
                save_publications(new_pubs)
            
            # Пост из пула
            current_time = time.time()
            interval_seconds = pool_interval * 60
            
            if current_time - last_pool_check >= interval_seconds:
                last_pool_check = current_time
                
                post, index = get_post_for_publishing()
                if post:
                    debug_log("PUBLISHER", f"Публикуем пост из пула (интервал {pool_interval} мин)")
                    success = publish_post(bot, tg_chat_id, vk_token, vk_owner_id, post)
                    if success:
                        send_report(bot, tg_chat_id, "✅ Пост из пула опубликован!")
                    else:
                        send_report(bot, tg_chat_id, "❌ Не удалось опубликовать пост из пула")
                else:
                    debug_log("PUBLISHER", "Нет постов в пуле", "WARNING")
                    send_report(bot, tg_chat_id, "⚠️ Нет постов в пуле для публикации")
            
        except Exception as e:
            debug_log("PUBLISHER", f"Ошибка в цикле: {e}", "ERROR")
            send_report(bot, tg_chat_id, f"❌ Ошибка публикатора: {e}")
        
        time.sleep(30)
