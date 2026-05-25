# ==========================================
# Файл: services/vk_uploader.py
# Справка: README.md → VK загрузка медиа
# Задача: загрузка и публикация постов в VK
# Комментарий: поддерживает одно или несколько фото, видео (экспериментально)
# Зависит от: requests, os, json
# Вызывается из: admin_commands.py (пост в VK)
# ==========================================

import os
import requests
import json
from debug_utils import debug_log

def get_vk_upload_url(vk_token, owner_id):
    """Получает URL для загрузки фото на стену VK"""
    params = {
        "access_token": vk_token,
        "v": "5.199",
        "owner_id": owner_id
    }
    try:
        r = requests.get("https://api.vk.com/method/photos.getWallUploadServer", params=params, timeout=10)
        data = r.json()
        if "response" in data:
            return data["response"].get("upload_url")
        else:
            debug_log("VK_UPLOADER", f"Ошибка получения upload URL: {data}", "ERROR")
            return None
    except Exception as e:
        debug_log("VK_UPLOADER", f"Ошибка: {e}", "ERROR")
        return None

def upload_photo_to_vk(upload_url, file_path, vk_token):
    """Загружает одно фото на полученный upload URL"""
    try:
        with open(file_path, 'rb') as f:
            files = {'photo': f}
            r = requests.post(upload_url, files=files, timeout=30)
            data = r.json()
        
        save_params = {
            "access_token": vk_token,
            "v": "5.199",
            "photo": data['photo'],
            "server": data['server'],
            "hash": data['hash']
        }
        r = requests.get("https://api.vk.com/method/photos.saveWallPhoto", params=save_params, timeout=30)
        photo_data = r.json()
        
        if 'response' in photo_data and photo_data['response']:
            photo = photo_data['response'][0]
            return f"photo{photo['owner_id']}_{photo['id']}"
        else:
            debug_log("VK_UPLOADER", f"Ошибка сохранения фото: {photo_data}", "ERROR")
            return None
    except Exception as e:
        debug_log("VK_UPLOADER", f"Ошибка загрузки фото: {e}", "ERROR")
        return None

def post_to_vk(message, vk_token, owner_id, file_paths=None):
    """
    Публикует пост в VK.
    
    Args:
        message: текст поста
        vk_token: токен VK
        owner_id: ID сообщества (отрицательное число)
        file_paths: путь к файлу (str) или список путей (list)
    
    Returns:
        (success, post_url_or_error)
    """
    if not vk_token or not owner_id:
        debug_log("VK_UPLOADER", "Нет токена или owner_id", "ERROR")
        return False, "❌ VK_TOKEN или VK_OWNER_ID не заданы"
    
    # Приводим file_paths к списку для единообразия
    if file_paths is None:
        file_paths = []
    elif isinstance(file_paths, str):
        file_paths = [file_paths]
    
    attachments = []
    
    # Загружаем файлы
    if file_paths:
        upload_url = get_vk_upload_url(vk_token, owner_id)
        if not upload_url:
            return False, "❌ Не удалось получить URL для загрузки"
        
        for fp in file_paths:
            if not os.path.exists(fp):
                debug_log("VK_UPLOADER", f"Файл не найден: {fp}", "WARNING")
                continue
            
            ext = os.path.splitext(fp)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                photo_att = upload_photo_to_vk(upload_url, fp, vk_token)
                if photo_att:
                    attachments.append(photo_att)
            else:
                debug_log("VK_UPLOADER", f"Неподдерживаемый тип файла: {ext}", "WARNING")
    
    # Отправляем пост
    params = {
        "access_token": vk_token,
        "v": "5.199",
        "owner_id": owner_id,
        "message": message,
        "from_group": 1
    }
    if attachments:
        params['attachments'] = ",".join(attachments)
        debug_log("VK_UPLOADER", f"Прикреплено {len(attachments)} вложений")
    
    try:
        r = requests.get("https://api.vk.com/method/wall.post", params=params, timeout=30)
        data = r.json()
        if 'response' in data:
            post_id = data['response']['post_id']
            post_url = f"https://vk.com/wall-{abs(owner_id)}_{post_id}"
            debug_log("VK_UPLOADER", f"✅ Пост опубликован: {post_url}")
            return True, post_url
        else:
            error_msg = data.get('error', {}).get('error_msg', 'неизвестная ошибка')
            debug_log("VK_UPLOADER", f"Ошибка VK: {error_msg}", "ERROR")
            return False, f"❌ Ошибка VK: {error_msg}"
    except Exception as e:
        debug_log("VK_UPLOADER", f"Исключение: {e}", "ERROR")
        return False, f"❌ Ошибка сети: {e}"
