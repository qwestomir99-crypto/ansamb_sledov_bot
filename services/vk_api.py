# ==========================================
# Файл: services/vk_api.py
# Справка: README.md → VK API
# Задача: комментарии, ответы, постинг в VK
# Комментарий: защищён от байтов и кривых данных
# ==========================================

import requests
from flask import Blueprint, request, jsonify
from debug_utils import debug_log
from services.secrets_manager import get_secret
from services.app import get_vk_token

vk_api_bp = Blueprint('vk_api', __name__)

# ==========================================
# ЗАЩИТНЫЕ ФУНКЦИИ
# ==========================================

def ensure_string(value, default=""):
    if value is None:
        return default
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin1')
    return str(value)

def ensure_int(value, default=0):
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        if isinstance(value, str):
            import re
            numbers = re.findall(r'-?\d+', value)
            if numbers:
                return int(numbers[0])
        return default

# ==========================================
# ЛОГИРОВАНИЕ
# ==========================================

def log_vk(level, message):
    debug_log("VK_API", message, level)

# ==========================================
# ТОКЕНЫ И ID
# ==========================================

def get_current_token():
    token = get_vk_token()
    return ensure_string(token)

def get_vk_owner_id():
    owner = get_secret("VK_OWNER_ID")
    return ensure_int(owner)

def get_vk_group_id():
    group = get_secret("VK_GROUP_ID")
    return ensure_int(group)

def get_vk_token_user():
    token = get_secret("VK_TOKEN_USER")
    return ensure_string(token)

def get_vk_access_token():
    token = get_secret("VK_ACCESS_TOKEN")
    return ensure_string(token)

# ==========================================
# ПУБЛИКАЦИЯ ПОСТА
# ==========================================

def get_post_params(text, target='group'):
    vk_owner_id = get_vk_owner_id()
    vk_group_id = get_vk_group_id()
    
    if target == 'group':
        owner_id = vk_group_id
        from_group = 1
        token = get_vk_token_user()
    else:
        owner_id = vk_owner_id
        from_group = 0
        token = get_vk_access_token()
    
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

# ==========================================
# API ENDPOINTS
# ==========================================

@vk_api_bp.route('/comment', methods=['POST'])
def api_vk_comment():
    data = request.json
    post_id = data.get('post_id')
    text = data.get('text', '').strip()
    token = get_current_token()
    vk_group_id = get_vk_group_id()
    
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
    vk_group_id = get_vk_group_id()
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
    vk_group_id = get_vk_group_id()
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
    vk_group_id = get_vk_group_id()
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
