# ==========================================
# Файл: services/vk_api.py
# Справка: README.md → Веб-морда / VK API
# Задача: API для комментариев, ответов и постинга в VK
# Комментарий: добавлена функция get_vk_messages() для фонового потока
# Зависит от: flask, requests, debug_utils
# Вызывается из: services/app.py (blueprint)
# ==========================================

import os
import requests
from flask import Blueprint, request, jsonify
from debug_utils import debug_log

vk_api_bp = Blueprint('vk_api', __name__)

VK_TOKEN = os.environ.get("VK_TOKEN")
try:
    VK_GROUP_ID = int(os.environ.get("VK_GROUP_ID", 0))
except (ValueError, TypeError):
    VK_GROUP_ID = 0

def log_vk(level, message):
    debug_log("VK_API", message, level)

@vk_api_bp.route('/comment', methods=['POST'])
def api_vk_comment():
    """
    Добавляет комментарий к посту в VK.
    Ожидает JSON: {"post_id": 123, "text": "текст комментария"}
    """
    data = request.json
    post_id = data.get('post_id')
    text = data.get('text', '').strip()
    
    if not VK_TOKEN or not VK_GROUP_ID:
        log_vk("ERROR", "VK_TOKEN или VK_GROUP_ID не заданы")
        return jsonify({"status": "error", "error": "VK не настроен"}), 500
    
    if not post_id or not text:
        return jsonify({"status": "error", "error": "post_id и text обязательны"}), 400
    
    params = {
        "access_token": VK_TOKEN,
        "v": "5.199",
        "owner_id": -VK_GROUP_ID,
        "post_id": post_id,
        "message": text
    }
    
    try:
        log_vk("INFO", f"Добавление комментария к посту {post_id}")
        r = requests.get("https://api.vk.com/method/wall.createComment", params=params, timeout=30)
        data = r.json()
        
        if 'response' in data:
            log_vk("INFO", f"Комментарий добавлен, ID: {data['response']}")
            return jsonify({"status": "ok", "comment_id": data['response']})
        else:
            error_msg = data.get('error', {}).get('error_msg', 'неизвестная ошибка')
            log_vk("ERROR", f"Ошибка VK: {error_msg}")
            return jsonify({"status": "error", "error": error_msg}), 500
    except Exception as e:
        log_vk("ERROR", f"Исключение: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@vk_api_bp.route('/send_message', methods=['POST'])
def api_vk_send_message():
    """
    Отправляет личное сообщение в VK.
    Ожидает JSON: {"peer_id": 123456789, "text": "текст сообщения"}
    """
    data = request.json
    peer_id = data.get('peer_id')
    text = data.get('text', '').strip()
    
    if not VK_TOKEN:
        log_vk("ERROR", "VK_TOKEN не задан")
        return jsonify({"status": "error", "error": "VK не настроен"}), 500
    
    if not peer_id or not text:
        return jsonify({"status": "error", "error": "peer_id и text обязательны"}), 400
    
    params = {
        "access_token": VK_TOKEN,
        "v": "5.199",
        "peer_id": peer_id,
        "message": text,
        "random_id": 0
    }
    
    try:
        log_vk("INFO", f"Отправка сообщения в чат {peer_id}")
        r = requests.get("https://api.vk.com/method/messages.send", params=params, timeout=30)
        data = r.json()
        
        if 'response' in data:
            log_vk("INFO", f"Сообщение отправлено, ID: {data['response']}")
            return jsonify({"status": "ok", "message_id": data['response']})
        else:
            error_msg = data.get('error', {}).get('error_msg', 'неизвестная ошибка')
            log_vk("ERROR", f"Ошибка VK: {error_msg}")
            return jsonify({"status": "error", "error": error_msg}), 500
    except Exception as e:
        log_vk("ERROR", f"Исключение: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@vk_api_bp.route('/like', methods=['POST'])
def api_vk_like():
    """
    Ставит лайк посту в VK.
    Ожидает JSON: {"post_id": 123, "owner_id": -123456789}
    """
    data = request.json
    post_id = data.get('post_id')
    owner_id = data.get('owner_id', -VK_GROUP_ID)
    
    if not VK_TOKEN:
        log_vk("ERROR", "VK_TOKEN не задан")
        return jsonify({"status": "error", "error": "VK не настроен"}), 500
    
    if not post_id:
        return jsonify({"status": "error", "error": "post_id обязателен"}), 400
    
    params = {
        "access_token": VK_TOKEN,
        "v": "5.199",
        "type": "post",
        "owner_id": owner_id,
        "item_id": post_id
    }
    
    try:
        log_vk("INFO", f"Лайк на пост {post_id}")
        r = requests.get("https://api.vk.com/method/likes.add", params=params, timeout=30)
        data = r.json()
        
        if 'response' in data:
            return jsonify({"status": "ok"})
        else:
            error_msg = data.get('error', {}).get('error_msg', 'неизвестная ошибка')
            return jsonify({"status": "error", "error": error_msg}), 500
    except Exception as e:
        log_vk("ERROR", f"Исключение: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@vk_api_bp.route('/repost', methods=['POST'])
def api_vk_repost():
    """
    Делает репост поста в VK.
    Ожидает JSON: {"post_id": 123, "owner_id": -123456789, "text": "мой комментарий"}
    """
    data = request.json
    post_id = data.get('post_id')
    owner_id = data.get('owner_id', -VK_GROUP_ID)
    text = data.get('text', '').strip()
    
    if not VK_TOKEN:
        log_vk("ERROR", "VK_TOKEN не задан")
        return jsonify({"status": "error", "error": "VK не настроен"}), 500
    
    if not post_id:
        return jsonify({"status": "error", "error": "post_id обязателен"}), 400
    
    params = {
        "access_token": VK_TOKEN,
        "v": "5.199",
        "object": f"wall{owner_id}_{post_id}"
    }
    if text:
        params["message"] = text
    
    try:
        log_vk("INFO", f"Репост поста {post_id}")
        r = requests.get("https://api.vk.com/method/wall.repost", params=params, timeout=30)
        data = r.json()
        
        if 'response' in data:
            return jsonify({"status": "ok", "repost_id": data['response']})
        else:
            error_msg = data.get('error', {}).get('error_msg', 'неизвестная ошибка')
            return jsonify({"status": "error", "error": error_msg}), 500
    except Exception as e:
        log_vk("ERROR", f"Исключение: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

# ==========================================
# ФУНКЦИЯ ДЛЯ ФОНОВОГО ПОТОКА
# ==========================================

def get_vk_messages(limit=10):
    """
    Получение последних сообщений из VK.
    Возвращает список сообщений в формате:
    [{'chat_id': 123, 'text': 'текст', 'timestamp': '2026-06-01T12:00:00', 'source': 'vk'}]
    """
    if not VK_TOKEN or not VK_GROUP_ID:
        log_vk("ERROR", "VK_TOKEN или VK_GROUP_ID не заданы")
        return []
    
    try:
        # Получаем последние сообщения из чатов
        params = {
            "access_token": VK_TOKEN,
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
# ДЛЯ ТЕСТА
# ==========================================
if __name__ == "__main__":
    print("VK API модуль загружен")
    print("Доступные эндпоинты:")
    print("  POST /api/vk/comment  - комментарий к посту")
    print("  POST /api/vk/send_message - личное сообщение")
    print("  POST /api/vk/like - лайк")
    print("  POST /api/vk/repost - репост")
