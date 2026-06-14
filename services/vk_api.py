# ==========================================
# Файл: services/vk_api.py
# Справка: README.md → Веб-морда / VK API
# Задача: API для комментариев, ответов и постинга в VK
# Комментарий: токен теперь берётся через get_vk_token() (автообновление)
# ==========================================

import sys
import os
import requests
from flask import Blueprint, request, jsonify
from debug_utils import debug_log
from services.app import get_vk_token
from services.secrets_manager import get_secret

vk_api_bp = Blueprint('vk_api', __name__)

def log_vk(level, message):
    debug_log("VK_API", message, level)

def get_current_token():
    token = get_vk_token()
    if not token:
        log_vk("ERROR", "Не удалось получить токен VK")
    return token

def get_post_params(text, target='group'):
    """
    Возвращает параметры для wall.post в зависимости от цели.
    target: 'group' (публикация в группу) или 'private' (публикация в личку)
    """
    # Исправление: принудительная конвертация в int
    vk_owner_id_str = get_secret("VK_OWNER_ID")
    vk_owner_id = int(vk_owner_id_str) if vk_owner_id_str else 0
    
    vk_group_id_str = get_secret("VK_GROUP_ID")
    vk_group_id = int(vk_group_id_str) if vk_group_id_str else 0
    
    if target == 'group':
        owner_id = vk_group_id
        from_group = 1
        token = get_secret("VK_TOKEN_USER")
    else:
        owner_id = vk_owner_id
        from_group = 0
        token = get_secret("VK_ACCESS_TOKEN")
    
    return {
        "access_token": token,
        "v": "5.199",
        "owner_id": owner_id,
        "message": text,
        "from_group": from_group
    }

def send_vk_post(text, target='group'):
    params = get_post_params(text, target)
    if not params["access_token"]:
        log_vk("ERROR", "Не удалось получить токен для публикации")
        return False
    
    try:
        log_vk("INFO", f"Отправка поста в VK (target={target})")
        r = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
        data = r.json()
        
        if 'response' in data:
            log_vk("INFO", f"Пост отправлен, ID: {data['response']['post_id']}")
            return True
        else:
            error_msg = data.get('error', {}).get('error_msg', 'неизвестная ошибка')
            log_vk("ERROR", f"Ошибка VK: {error_msg}")
            return False
    except Exception as e:
        log_vk("ERROR", f"Исключение: {e}")
        return False

@vk_api_bp.route('/comment', methods=['POST'])
def api_vk_comment():
    data = request.json
    post_id = data.get('post_id')
    text = data.get('text', '').strip()
    token = get_current_token()
    
    # Исправление: принудительная конвертация в int
    vk_group_id_str = get_secret("VK_GROUP_ID")
    vk_group_id = int(vk_group_id_str) if vk_group_id_str else 0
    
    if not token or not vk_group_id:
        return jsonify({"status": "error", "error": "VK не настроен"}), 500
    if not post_id or not text:
        return jsonify({"status": "error", "error": "post_id и text обязательны"}), 400
    params = {
        "access_token": token,
        "v": "5.199",
        "owner_id": -vk_group_id,
        "post_id": post_id,
        "message": text
    }
    try:
        r = requests.get("https://api.vk.com/method/wall.createComment", params=params, timeout=30)
        data = r.json()
        if 'response' in data:
            return jsonify({"status": "ok", "comment_id": data['response']})
        else:
            return jsonify({"status": "error", "error": data.get('error', {}).get('error_msg', '')}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@vk_api_bp.route('/send_message', methods=['POST'])
def api_vk_send_message():
    data = request.json
    peer_id = data.get('peer_id')
    text = data.get('text', '').strip()
    token = get_current_token()
    if not token:
        return jsonify({"status": "error", "error": "VK не настроен"}), 500
    if not peer_id or not text:
        return jsonify({"status": "error", "error": "peer_id и text обязательны"}), 400
    params = {
        "access_token": token,
        "v": "5.199",
        "peer_id": peer_id,
        "message": text,
        "random_id": 0
    }
    try:
        r = requests.get("https://api.vk.com/method/messages.send", params=params, timeout=30)
        data = r.json()
        if 'response' in data:
            return jsonify({"status": "ok", "message_id": data['response']})
        else:
            return jsonify({"status": "error", "error": data.get('error', {}).get('error_msg', '')}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@vk_api_bp.route('/like', methods=['POST'])
def api_vk_like():
    data = request.json
    post_id = data.get('post_id')
    
    # Исправление: принудительная конвертация в int
    vk_group_id_str = get_secret("VK_GROUP_ID")
    vk_group_id = int(vk_group_id_str) if vk_group_id_str else 0
    
    owner_id = data.get('owner_id', -vk_group_id if vk_group_id else 0)
    token = get_current_token()
    if not token:
        return jsonify({"status": "error", "error": "VK не настроен"}), 500
    if not post_id:
        return jsonify({"status": "error", "error": "post_id обязателен"}), 400
    params = {
        "access_token": token,
        "v": "5.199",
        "type": "post",
        "owner_id": owner_id,
        "item_id": post_id
    }
    try:
        r = requests.get("https://api.vk.com/method/likes.add", params=params, timeout=30)
        data = r.json()
        if 'response' in data:
            return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "error": data.get('error', {}).get('error_msg', '')}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@vk_api_bp.route('/repost', methods=['POST'])
def api_vk_repost():
    data = request.json
    post_id = data.get('post_id')
    
    # Исправление: принудительная конвертация в int
    vk_group_id_str = get_secret("VK_GROUP_ID")
    vk_group_id = int(vk_group_id_str) if vk_group_id_str else 0
    
    owner_id = data.get('owner_id', -vk_group_id if vk_group_id else 0)
    text = data.get('text', '').strip()
    token = get_current_token()
    if not token:
        return jsonify({"status": "error", "error": "VK не настроен"}), 500
    if not post_id:
        return jsonify({"status": "error", "error": "post_id обязателен"}), 400
    params = {
        "access_token": token,
        "v": "5.199",
        "object": f"wall{owner_id}_{post_id}"
    }
    if text:
        params["message"] = text
    try:
        r = requests.get("https://api.vk.com/method/wall.repost", params=params, timeout=30)
        data = r.json()
        if 'response' in data:
            return jsonify({"status": "ok", "repost_id": data['response']})
        else:
            return jsonify({"status": "error", "error": data.get('error', {}).get('error_msg', '')}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

def get_vk_messages(limit=10):
    token = get_current_token()
    vk_group_id_str = get_secret("VK_GROUP_ID")
    vk_group_id = int(vk_group_id_str) if vk_group_id_str else 0
    if not token or not vk_group_id:
        log_vk("ERROR", "VK_TOKEN или VK_GROUP_ID не заданы")
        return []
    try:
        params = {
            "access_token": token,
            "v": "5.199",
            "count": limit,
            "filter": "all"
        }
        r = requests.get("https://api.vk.com/method/messages.get", params=params, timeout=30)
        data = r.json()
        messages = []
        if 'response' in data and 'items' in data['response']:
            for item in data['response']['items']:
                messages.append({
                    'chat_id': item.get('peer_id', 0),
                    'text': item.get('text', ''),
                    'timestamp': item.get('date', ''),
                    'source': 'vk'
                })
        return messages
    except Exception as e:
        log_vk("ERROR", f"Ошибка получения сообщений: {e}")
        return []

if __name__ == "__main__":
    print("VK API модуль загружен")
