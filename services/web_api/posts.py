# ==========================================
# Файл: services/web_api/posts.py
# Справка: README.md → Веб-морда / API / Посты
# Задача: эндпоинты для создания постов в TG и VK
# Комментарий: использует tg_api и vk_api для реальной отправки
# Зависит от: flask, debug_utils, services.tg_api, services.vk_api
# Вызывается из: web_api/__init__.py
# ==========================================

from flask import Blueprint, request, jsonify
from debug_utils import debug_log

posts_bp = Blueprint('posts', __name__)

def log_posts(level, message):
    debug_log("WEB_API_POSTS", message, level)

@posts_bp.route('/create', methods=['POST'])
def create_post():
    """Создаёт пост в Telegram или VK"""
    data = request.json
    platform = data.get('platform')
    text = data.get('text', '').strip()
    
    if not platform or not text:
        return jsonify({"status": "error", "error": "platform и text обязательны"}), 400
    
    try:
        if platform == 'telegram':
            from services.tg_api import tg_request
            import os
            channel = os.environ.get("PUBLISH_CHANNEL", "@qwestomir")
            params = {"chat_id": channel, "text": text, "parse_mode": "Markdown"}
            result = tg_request("sendMessage", params)
            if result:
                log_posts("INFO", f"Пост в Telegram отправлен")
                return jsonify({"status": "ok", "message": "Пост опубликован в Telegram"})
            else:
                return jsonify({"status": "error", "error": "Ошибка отправки в Telegram"}), 500
                
        elif platform == 'vk':
            from services.vk_api import VK_TOKEN, VK_GROUP_ID
            import requests
            
            if not VK_TOKEN or not VK_GROUP_ID:
                return jsonify({"status": "error", "error": "VK не настроен"}), 500
            
            params = {
                "access_token": VK_TOKEN,
                "v": "5.199",
                "owner_id": -VK_GROUP_ID,
                "message": text,
                "from_group": 1
            }
            r = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
            resp_data = r.json()
            
            if 'response' in resp_data:
                post_id = resp_data['response']['post_id']
                log_posts("INFO", f"Пост в VK отправлен, ID: {post_id}")
                return jsonify({"status": "ok", "message": "Пост опубликован в VK", "post_id": post_id})
            else:
                error_msg = resp_data.get('error', {}).get('error_msg', 'неизвестная ошибка')
                return jsonify({"status": "error", "error": error_msg}), 500
        else:
            return jsonify({"status": "error", "error": "Неверная платформа"}), 400
            
    except Exception as e:
        log_posts("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

@posts_bp.route('/vk', methods=['POST'])
def post_to_vk():
    """Пост в VK (текст) — кнопка «Отправить» в карточке VK"""
    data = request.json
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({"status": "error", "error": "text обязателен"}), 400
    
    try:
        from services.vk_api import VK_TOKEN, VK_GROUP_ID
        import requests
        
        if not VK_TOKEN or not VK_GROUP_ID:
            return jsonify({"status": "error", "error": "VK не настроен"}), 500
        
        params = {
            "access_token": VK_TOKEN,
            "v": "5.199",
            "owner_id": -VK_GROUP_ID,
            "message": text,
            "from_group": 1
        }
        r = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
        resp_data = r.json()
        
        if 'response' in resp_data:
            post_id = resp_data['response']['post_id']
            log_posts("INFO", f"Пост в VK отправлен, ID: {post_id}")
            return jsonify({
                "status": "ok", 
                "message": "Пост опубликован в VK",
                "url": f"https://vk.com/wall-{VK_GROUP_ID}_{post_id}"
            })
        else:
            error_msg = resp_data.get('error', {}).get('error_msg', 'неизвестная ошибка')
            return jsonify({"status": "error", "error": error_msg}), 500
            
    except Exception as e:
        log_posts("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

@posts_bp.route('/telegram', methods=['POST'])
def post_to_telegram():
    """Пост в Telegram — отдельный эндпоинт"""
    data = request.json
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({"status": "error", "error": "text обязателен"}), 400
    
    try:
        from services.tg_api import tg_request
        import os
        channel = os.environ.get("PUBLISH_CHANNEL", "@qwestomir")
        params = {"chat_id": channel, "text": text, "parse_mode": "Markdown"}
        result = tg_request("sendMessage", params)
        if result:
            log_posts("INFO", "Пост в Telegram отправлен")
            return jsonify({"status": "ok", "message": "Пост опубликован в Telegram"})
        else:
            return jsonify({"status": "error", "error": "Ошибка отправки в Telegram"}), 500
            
    except Exception as e:
        log_posts("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500
