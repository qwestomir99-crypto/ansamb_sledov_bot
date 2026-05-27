# ==========================================
# Файл: services/web_api/alice.py
# Справка: README.md → Веб-морда / API / Алиса
# Задача: эндпоинты для управления Алисой
# Комментарий: часть web_api, вынесена в отдельный модуль
# Зависит от: flask, debug_utils, Alice.alice_admin
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, request, jsonify
from debug_utils import debug_log
from Alice.alice_admin import load_config, save_config

alice_bp = Blueprint('alice', __name__)

def log_a(level, message):
    debug_log("WEB_API_ALICE", message, level)

@alice_bp.route('/toggle', methods=['POST'])
def toggle_alice():
    config = load_config()
    if "alice" not in config:
        config["alice"] = {}
    config["alice"]["enabled"] = not config.get("alice", {}).get("enabled", False)
    save_config(config)
    log_a("INFO", f"Алиса {'включена' if config['alice']['enabled'] else 'выключена'}")
    return jsonify({"status": "ok", "enabled": config["alice"]["enabled"]})
