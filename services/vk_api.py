# ==========================================
# Файл: services/vk_api.py
# Справка: README.md → Веб-морда / VK API
# Задача: API для комментариев, ответов и постинга в VK
# Комментарий: токен теперь берётся через get_vk_token() (автообновление)
# ==========================================

import os
import requests
from flask import Blueprint, request, jsonify
from debug_utils import debug_log
from services.app import get_vk_token

vk_api_bp = Blueprint('vk_api', __name__)

# ID группы из переменных окружения
try:
    VK_GROUP_ID = int(os.environ.get("VK_GROUP_ID", 0))
except (ValueError, TypeError):
    VK_GROUP_ID = 0

def log_vk(level, message):
    debug_log("VK_API", message, level)

def get_current_token():
    token = get_vk_token()
    if not token:
        log_vk("ERROR", "Не удалось получить токен VK")
    return token

# ==========================================
# Вспомогательная функция для выбора токена и владельца
# ==========================================

def get_post_params(text, target='group'):
    """
    Возвращает параметры для wall.post в зависимости от цели.
    target: 'group' (публикация в группу) или 'private' (публикация в личку)
    """
    vk_owner_id = os.environ.get("VK_OWNER_ID")      # твой личный ID (для чтения)
    vk_group_id = os.environ.get("VK_GROUP_ID")      # ID группы (для публикации)
    
    if target == 'group':
        owner_id = int(vk_group_id)
        from_group = 1
        token = os.environ.get("VK_TOKEN_USER")      # групповой ключ
    else:
        owner_id = int(vk_owner_id)
        from_group = 0
        token = os.environ.get("VK_ACCESS_TOKEN")    # личный ключ
    
    return {
        "access_token": token,
        "v": "5.199",
        "owner_id": owner_id,
        "message": text,
        "from_group": from_group
    }

# ==========================================
# Публикация поста (основная функция)
# ==========================================

def send_vk_post(text, target='group'):
    """
    Отправляет пост на стену VK.
    target='group' → пост в группу (коммерция)
    target='private' → пост в личку (творчество)
    Возвращает True/False.
    """
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
# Остальные API-методы (комментарии, лайки, репосты, сообщения)
# ==========================================

@vk_api_bp.route('/comment', methods=['POST'])
def api_vk_comment():
    data = request.json
    post_id = data.get('post_id')
    text = data.get('text', '').strip()
    token = get_current_token()
    if not token or not VK_GROUP_ID:
        return jsonify({"status": "error", "error": "VK не настроен"}), 500
    if not post_id or not text:
        return jsonify({"status": "error", "error": "post_id и text обязательны"}), 400
    params = {
        "access_token": token,
        "v": "5.199",
        "owner_id": -VK_GROUP_ID,
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
    owner_id = data.get('owner_id', -VK_GROUP_ID)
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
    owner_id = data.get('owner_id', -VK_GROUP_ID)
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

# ==========================================
# Фоновый поток (получение сообщений)
# ==========================================

def get_vk_messages(limit=10):
    token = get_current_token()
    if not token or not VK_GROUP_ID:
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

# ==========================================
# Тест
# ==========================================
if __name__ == "__main__":
    print("VK API модуль загружен")
