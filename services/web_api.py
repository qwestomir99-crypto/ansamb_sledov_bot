# ==========================================
# Файл: services/web_api.py
# Справка: README.md → Веб-морда / API
# Задача: API для управления ботом, режимами, цитатами, настроением, аудитом, темами
# Комментарий: используется веб-мордой для панели управления
# Зависит от: flask, debug_utils, ping_utils, debug_audit, theme, tg_api, vk_api
# Вызывается из: services/app.py (blueprint)
# ==========================================

import os
import json
from flask import Blueprint, request, jsonify, session, redirect, url_for
from functools import wraps
from debug_utils import debug_log

web_api = Blueprint('web_api', __name__)

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def log_web(level, message):
    debug_log("WEB_API", message, level)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ==========================================
# ПУТИ К ФАЙЛАМ
# ==========================================
QUOTES_FILE = "dialogue/data/quotes.txt"
MODE_FILE = "dialogue/data/mode.txt"
MOOD_FILE = "dialogue/data/mood.txt"

# ==========================================
# РАБОТА С ЦИТАТАМИ
# ==========================================
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

# ==========================================
# РАБОТА С РЕЖИМАМИ
# ==========================================
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

# ==========================================
# РАБОТА С НАСТРОЕНИЕМ
# ==========================================
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
@login_required
def api_state():
    """Возвращает текущее состояние (режим, цитаты)"""
    return jsonify({
        "mode": get_current_mode(),
        "quotes": get_quotes()
    })

@web_api.route('/set_mode', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def api_get_mood():
    """Возвращает текущее настроение агента"""
    return jsonify({"status": "ok", "mood": get_current_mood()})

@web_api.route('/toggle_ping', methods=['POST'])
@login_required
def api_toggle_ping():
    """Включает/выключает пинг бота"""
    try:
        from ping_utils import toggle_ping
        new_state = toggle_ping()
        log_web("INFO", f"Пинг {'включён' if new_state else 'выключён'}")
        return jsonify({"status": "ok", "message": f"Пинг {'включён' if new_state else 'выключён'}"})
    except ImportError:
        return jsonify({"status": "error", "message": "ping_utils.py не найден"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_api.route('/add_quote', methods=['POST'])
@login_required
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
@login_required
def api_create_post():
    """Создаёт новый пост в Telegram или VK"""
    data = request.json
    platform = data.get('platform')
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({"status": "error", "error": "Пустой текст"}), 400
    
    if platform == 'telegram':
        try:
            from services.tg_api import send_telegram_message
            success = send_telegram_message(text)
            if success:
                return jsonify({"status": "ok", "message": "Пост отправлен в Telegram"})
            return jsonify({"status": "error", "message": "Ошибка отправки в Telegram"}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    elif platform == 'vk':
        try:
            from services.vk_api import send_vk_post
            success = send_vk_post(text)
            if success:
                return jsonify({"status": "ok", "message": "Пост отправлен в VK"})
            return jsonify({"status": "error", "message": "Ошибка отправки в VK"}), 500
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "error": "Invalid platform"}), 400

# ==========================================
# УПРАВЛЕНИЕ ТЕМОЙ
# ==========================================
@web_api.route('/set_theme', methods=['POST'])
@login_required
def api_set_theme():
    """Сохраняет выбранную тему пользователя"""
    data = request.json
    theme = data.get('theme')
    if theme not in ['macos.css', 'dark.css']:
        return jsonify({"status": "error", "error": "Invalid theme"}), 400
    
    from services.theme import save_theme
    save_theme(theme)
    log_web("INFO", f"Тема изменена на {theme}")
    return jsonify({"status": "ok", "theme": theme})

# ==========================================
# АУДИТ И ИНДЕКС
# ==========================================
@web_api.route('/audit/run', methods=['POST'])
@login_required
def api_audit_run():
    """Запускает аудит"""
    try:
        from debug_audit import run_audit
        result = run_audit()
        if result:
            return jsonify({"status": "ok", "message": "Аудит выполнен", "results": result})
        return jsonify({"status": "error", "message": "Ошибка выполнения аудита"}), 500
    except ImportError:
        return jsonify({"status": "error", "message": "debug_audit.py не найден"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_api.route('/audit/status', methods=['GET'])
@login_required
def api_audit_status():
    """Возвращает статус последнего аудита"""
    from debug_utils import get_audit_status
    return jsonify(get_audit_status())

@web_api.route('/audit/index', methods=['GET'])
@login_required
def api_audit_index():
    """Возвращает содержимое debug_index.json"""
    index_file = "debug_index.json"
    if not os.path.exists(index_file):
        return jsonify({"status": "ok", "index": {}})
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({"status": "ok", "index": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@web_api.route('/audit/logs/stats', methods=['GET'])
@login_required
def api_audit_log_stats():
    """Возвращает статистику по логам"""
    try:
        from debug_audit import analyze_logs
        return jsonify(analyze_logs())
    except ImportError:
        return jsonify({"status": "ok", "stats": {}})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
