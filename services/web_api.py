# ==========================================
# Файл: services/web_api.py
# Справка: README.md → Веб-морда / API
# Задача: API для управления ботом, режимами, цитатами, настроением
# Комментарий: используется веб-мордой для панели управления
# Зависит от: flask, debug_utils, ping_utils
# Вызывается из: services/app.py (blueprint)
# ==========================================

import os
import json
from flask import Blueprint, request, jsonify
from debug_utils import debug_log

web_api = Blueprint('web_api', __name__)

# ==========================================
# ПУТИ К ФАЙЛАМ
# ==========================================
QUOTES_FILE = "dialogue/data/quotes.txt"
MODE_FILE = "dialogue/data/mode.txt"
MOOD_FILE = "dialogue/data/mood.txt"

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def log_web(level, message):
    debug_log("WEB_API", message, level)

def get_quotes():
    try:
        with open(QUOTES_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()][-10:]
    except:
        return []

def add_quote(quote):
    try:
        os.makedirs(os.path.dirname(QUOTES_FILE), exist_ok=True)
        with open(QUOTES_FILE, "a", encoding="utf-8") as f:
            f.write(quote.strip() + "\n")
        return True
    except Exception as e:
        log_web("ERROR", f"Ошибка добавления цитаты: {e}")
        return False

def get_current_mode():
    try:
        with open(MODE_FILE, "r") as f:
            return f.read().strip()
    except:
        return "день"

def set_current_mode(mode):
    try:
        os.makedirs(os.path.dirname(MODE_FILE), exist_ok=True)
        with open(MODE_FILE, "w") as f:
            f.write(mode)
        return True
    except Exception as e:
        log_web("ERROR", f"Ошибка сохранения режима: {e}")
        return False

def get_current_mood():
    try:
        with open(MOOD_FILE, "r") as f:
            return f.read().strip()
    except:
        return "artist"

def set_current_mood(mood):
    try:
        os.makedirs(os.path.dirname(MOOD_FILE), exist_ok=True)
        with open(MOOD_FILE, "w") as f:
            f.write(mood)
        return True
    except Exception as e:
        log_web("ERROR", f"Ошибка сохранения настроения: {e}")
        return False

# ==========================================
# API МАРШРУТЫ
# ==========================================

@web_api.route('/state', methods=['GET'])
def api_state():
    """Возвращает текущее состояние (режим, цитаты)"""
    return jsonify({
        "mode": get_current_mode(),
        "quotes": get_quotes()
    })

@web_api.route('/set_mode', methods=['POST'])
def api_set_mode():
    """Устанавливает режим бота (утро/день/вечер/ночь)"""
    data = request.json
    mode = data.get('mode')
    if mode in ['утро', 'день', 'вечер', 'ночь']:
        set_current_mode(mode)
        log_web("INFO", f"Режим изменён на {mode}")
        return jsonify({"status": "ok", "mode": mode})
    return jsonify({"status": "error", "error": "Invalid mode"}), 400

@web_api.route('/set_mood', methods=['POST'])
def api_set_mood():
    """Устанавливает настроение агента (artist/admin/poet/engineer)"""
    data = request.json
    mood = data.get('mood')
    if mood in ['artist', 'admin', 'poet', 'engineer']:
        set_current_mood(mood)
        log_web("INFO", f"Настроение изменено на {mood}")
        return jsonify({"status": "ok", "mood": mood})
    return jsonify({"status": "error", "error": "Invalid mood"}), 400

@web_api.route('/get_mood', methods=['GET'])
def api_get_mood():
    """Возвращает текущее настроение агента"""
    return jsonify({"status": "ok", "mood": get_current_mood()})

@web_api.route('/toggle_ping', methods=['POST'])
def api_toggle_ping():
    """Включает/выключает пинг бота"""
    try:
        from ping_utils import toggle_ping
        new_state = toggle_ping()
        log_web("INFO", f"Пинг {'включён' if new_state else 'выключён'}")
        return jsonify({"status": "ok", "message": f"Пинг {'включён' if new_state else 'выключён'}"})
    except Exception as e:
        log_web("ERROR", f"Ошибка переключения пинга: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@web_api.route('/add_quote', methods=['POST'])
def api_add_quote():
    """Добавляет новую цитату"""
    data = request.json
    quote = data.get('quote', '').strip()
    if not quote:
        return jsonify({"status": "error", "error": "Пустая цитата"}), 400
    if add_quote(quote):
        log_web("INFO", f"Добавлена цитата: {quote[:50]}")
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "error": "Ошибка сохранения"}), 500

@web_api.route('/create_post', methods=['POST'])
def api_create_post():
    """
    Создаёт новый пост в Telegram или VK.
    Ожидает JSON: {"platform": "telegram" или "vk", "text": "текст поста"}
    """
    data = request.json
    platform = data.get('platform')
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({"status": "error", "error": "Пустой текст"}), 400
    
    if platform == 'telegram':
        # Отправляем в Telegram (через бота)
        bot_token = os.environ.get("BOT_TOKEN")
        publish_channel = os.environ.get("PUBLISH_CHANNEL", "@qwestomir")
        if not bot_token:
            return jsonify({"status": "error", "error": "Telegram бот не настроен"}), 500
        try:
            import telebot
            bot = telebot.TeleBot(bot_token)
            bot.send_message(publish_channel, text, parse_mode='Markdown')
            log_web("INFO", f"Пост в Telegram отправлен: {text[:50]}")
            return jsonify({"status": "ok", "message": "Пост отправлен в Telegram"})
        except Exception as e:
            log_web("ERROR", f"Ошибка отправки в Telegram: {e}")
            return jsonify({"status": "error", "error": str(e)}), 500
    
    elif platform == 'vk':
        # Отправляем в VK
        vk_token = os.environ.get("VK_TOKEN")
        vk_group_id = os.environ.get("VK_GROUP_ID")
        if not vk_token or not vk_group_id:
            return jsonify({"status": "error", "error": "VK не настроен"}), 500
        try:
            import vk_api
            vk_session = vk_api.VkApi(token=vk_token)
            vk = vk_session.get_api()
            post = vk.wall.post(owner_id=-int(vk_group_id), message=text, from_group=1)
            post_url = f"https://vk.com/wall-{abs(int(vk_group_id))}_{post['post_id']}"
            log_web("INFO", f"Пост в VK опубликован: {post_url}")
            return jsonify({"status": "ok", "message": "Пост отправлен в VK", "url": post_url})
        except Exception as e:
            log_web("ERROR", f"Ошибка отправки в VK: {e}")
            return jsonify({"status": "error", "error": str(e)}), 500
    
    else:
        return jsonify({"status": "error", "error": "Invalid platform"}), 400

@web_api.route('/get_quote_stats', methods=['GET'])
def api_get_quote_stats():
    """Возвращает статистику по цитатам (количество)"""
    quotes = get_quotes()
    total = len(quotes)
    return jsonify({"status": "ok", "total": total, "last_10": quotes})

@web_api.route('/clear_quotes', methods=['POST'])
def api_clear_quotes():
    """Очищает все цитаты (только для админа)"""
    try:
        os.makedirs(os.path.dirname(QUOTES_FILE), exist_ok=True)
        with open(QUOTES_FILE, "w") as f:
            f.write("")
        log_web("INFO", "Все цитаты очищены")
        return jsonify({"status": "ok"})
    except Exception as e:
        log_web("ERROR", f"Ошибка очистки цитат: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

# ==========================================
# ДЛЯ ТЕСТА
# ==========================================
if __name__ == "__main__":
    print("WEB API модуль загружен")
    print("Доступные эндпоинты:")
    print("  GET /api/state - состояние бота")
    print("  POST /api/set_mode - установить режим")
    print("  POST /api/set_mood - установить настроение")
    print("  GET /api/get_mood - получить настроение")
    print("  POST /api/toggle_ping - переключить пинг")
    print("  POST /api/add_quote - добавить цитату")
    print("  POST /api/create_post - создать пост")
    print("  GET /api/get_quote_stats - статистика цитат")
    print("  POST /api/clear_quotes - очистить цитаты")
