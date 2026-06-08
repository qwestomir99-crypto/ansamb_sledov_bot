# ==========================================
# Файл: services/web_api/modes.py
# Справка: README.md → Веб-морда / API / Режимы
# Задача: эндпоинты для управления режимами и настроением
# Комментарий: добавлена защита @login_required
# Зависит от: flask, debug_utils
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, request, jsonify
from debug_utils import debug_log
from services.app import login_required
import os

modes_bp = Blueprint('modes', __name__)

def log_m(level, message):
    debug_log("WEB_API_MODES", message, level)

MODE_FILE = "dialogue/data/mode.txt"
MOOD_FILE = "dialogue/data/mood.txt"

def get_mode():
    try:
        with open(MODE_FILE, "r") as f:
            return f.read().strip()
    except:
        return "день"

def set_mode(mode):
    try:
        os.makedirs(os.path.dirname(MODE_FILE), exist_ok=True)
        with open(MODE_FILE, "w") as f:
            f.write(mode)
        return True
    except:
        return False

def get_mood():
    try:
        with open(MOOD_FILE, "r") as f:
            return f.read().strip()
    except:
        return "artist"

def set_mood(mood):
    try:
        os.makedirs(os.path.dirname(MOOD_FILE), exist_ok=True)
        with open(MOOD_FILE, "w") as f:
            f.write(mood)
        return True
    except:
        return False

@modes_bp.route('/state', methods=['GET'])
@login_required
def state():
    return jsonify({
        "mode": get_mode(),
        "mood": get_mood()
    })

@modes_bp.route('/set_mode', methods=['POST'])
@login_required
def set_mode_ep():
    data = request.json
    mode = data.get('mode')
    if mode in ['утро', 'день', 'вечер', 'ночь']:
        set_mode(mode)
        log_m("INFO", f"Режим изменён на {mode}")
        return jsonify({"status": "ok", "mode": mode})
    return jsonify({"status": "error", "error": "Неверный режим"}), 400

@modes_bp.route('/set_mood', methods=['POST'])
@login_required
def set_mood_ep():
    data = request.json
    mood = data.get('mood')
    if mood in ['artist', 'admin', 'poet', 'engineer']:
        set_mood(mood)
        log_m("INFO", f"Настроение изменено на {mood}")
        return jsonify({"status": "ok", "mood": mood})
    return jsonify({"status": "error", "error": "Неверное настроение"}), 400
