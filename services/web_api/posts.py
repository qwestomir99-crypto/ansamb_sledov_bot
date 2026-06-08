# ==========================================
# Файл: services/web_api/posts.py
# Справка: README.md → Веб-морда / API / Посты
# Задача: эндпоинты для создания постов в TG и VK
# Комментарий: добавлена защита @login_required
# Зависит от: flask, debug_utils, services.tg_api
# Вызывается из: web_api/__init__.py
# ==========================================

import os
import requests
from flask import Blueprint, request, jsonify
from debug_utils import debug_log
from services.app import login_required

posts_bp = Blueprint('posts', __name__)

def log_posts(level, message):
    debug_log("WEB_API_POSTS", message, level)

@posts_bp.route('/create', methods=['POST'])
@login_required
def create_post():
    """Создаёт пост в Telegram или VK (личный профиль)"""
    data = request.json
    platform = data.get('platform')
    text = data.get('text', '').strip()
    
    if not platform or not text:
        return jsonify({"status": "error", "error": "platform и text обязательны"}), 400
    
    try:
        if platform == 'telegram':
            from services.tg_api import tg_request
            channel = os.environ.get("PUBLISH_CHANNEL", "@qwestomir")
            params = {"chat_id": channel, "text": text, "parse_mode": "Markdown"}
            result = tg_request("sendMessage", params)
            if result:
                log_posts("INFO", "Пост в Telegram отправлен")
                return jsonify({"status": "ok", "message": "Пост опубликован в Telegram"})
            else:
                return jsonify({"status": "error", "error": "Ошибка отправки в Telegram"}), 500
                
        elif platform == 'vk':
            vk_token = os.environ.get("VK_USER_TOKEN")
            vk_owner_id = os.environ.get("VK_OWNER_ID")
            
            if not vk_token or not vk_owner_id:
                return jsonify({"status": "error", "error": "VK не настроен"}), 500
            
            params = {
                "access_token": vk_token,
                "v": "5.199",
                "owner_id": int(vk_owner_id),
                "message": text
            }
            r = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
            resp_data = r.json()
            
            if 'response' in resp_data:
                post_id = resp_data['response']['post_id']
                log_posts("INFO", f"Пост в VK отправлен, ID: {post_id}")
                return jsonify({"status": "ok", "message": "Пост опубликован в VK", "post_id": post_id})
            else:
                error_msg = resp_data.get('error', {}).get('error_msg', 'неизвестная ошибка')
                log_posts("ERROR", f"Ошибка VK: {error_msg}")
                return jsonify({"status": "error", "error": error_msg}), 500
        else:
            return jsonify({"status": "error", "error": "Неверная платформа"}), 400
            
    except Exception as e:
        log_posts("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

@posts_bp.route('/vk', methods=['POST'])
@login_required
def post_to_vk():
    """Пост в VK (текст) — личный профиль."""
    data = request.json
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({"status": "error", "error": "text обязателен"}), 400
    
    try:
        vk_token = os.environ.get("VK_USER_TOKEN")
        vk_owner_id = os.environ.get("VK_OWNER_ID")
        
        if not vk_token or not vk_owner_id:
            return jsonify({"status": "error", "error": "VK не настроен"}), 500
        
        params = {
            "access_token": vk_token,
            "v": "5.199",
            "owner_id": int(vk_owner_id),
            "message": text
        }
        r = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
        resp_data = r.json()
        
        if 'response' in resp_data:
            post_id = resp_data['response']['post_id']
            log_posts("INFO", f"Пост в VK отправлен, ID: {post_id}")
            return jsonify({
                "status": "ok",
                "message": "Пост опубликован в VK",
                "url": f"https://vk.com/wall{int(vk_owner_id)}_{post_id}"
            })
        else:
            error_msg = resp_data.get('error', {}).get('error_msg', 'неизвестная ошибка')
            log_posts("ERROR", f"Ошибка VK: {error_msg}")
            return jsonify({"status": "error", "error": error_msg}), 500
            
    except Exception as e:
        log_posts("ERROR", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

@posts_bp.route('/telegram', methods=['POST'])
@login_required
def post_to_telegram():
    """Пост в Telegram — отдельный эндпоинт"""
    data = request.json
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({"status": "error", "error": "text обязателен"}), 400
    
    try:
        from services.tg_api import tg_request
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
