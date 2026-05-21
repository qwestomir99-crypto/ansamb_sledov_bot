# ==========================================
# Файл: services/vk_uploader.py
# Справка: README.md → Загрузка видео в VK
# Задача: выбирает способ загрузки в зависимости от размера файла
# Комментарий: для видео >50 МБ требуется Userbot (Telethon) — заглушка
# Зависит от: requests, os, debug_utils
# Вызывается из: dialogue/admin/posts.py
# ==========================================

import os
import requests
from debug_utils import debug_log

def upload_video_to_vk(file_path, vk_token, vk_owner_id, text, tags):
    """
    Загружает видео в VK.
    - Если файл < 50 МБ → через VK API (прямая загрузка)
    - Если файл > 50 МБ → через Userbot (Telethon) — пока заглушка
    """
    try:
        file_size = os.path.getsize(file_path)
        size_mb = file_size / (1024 * 1024)
        debug_log("VK_UPLOADER", f"Файл: {file_path}, размер: {size_mb:.1f} МБ")
        
        if size_mb <= 50:
            debug_log("VK_UPLOADER", "Используем VK API (прямую загрузку)")
            return upload_via_vk_api(file_path, vk_token, vk_owner_id, text, tags)
        else:
            debug_log("VK_UPLOADER", "⚠️ Видео больше 50 МБ — требуется Userbot (Telethon). Заглушка.")
            # TODO: Реализовать загрузку через Userbot
            # from services.userbot_uploader import upload_via_userbot
            # return upload_via_userbot(file_path, text, tags)
            return False, "Видео >50 МБ, загрузка через Userbot пока не реализована"
    except Exception as e:
        debug_log("VK_UPLOADER", f"Ошибка при определении размера: {e}", "ERROR")
        return False, str(e)

def upload_via_vk_api(file_path, vk_token, vk_owner_id, text, tags):
    """Загрузка видео через VK API (для файлов до 50 МБ)"""
    try:
        # 1. Получаем upload URL
        params = {
            "access_token": vk_token,
            "v": "5.199",
            "name": text[:100],
            "description": tags,
            "owner_id": vk_owner_id,
            "is_private": 0
        }
        
        r = requests.get("https://api.vk.com/method/video.save", params=params, timeout=30)
        data = r.json()
        
        if "error" in data:
            error_msg = data["error"]["error_msg"]
            debug_log("VK_UPLOADER", f"Ошибка video.save: {error_msg}", "ERROR")
            return False, error_msg
        
        upload_url = data["response"]["upload_url"]
        video_id = data["response"]["video_id"]
        owner_id_resp = data["response"]["owner_id"]
        debug_log("VK_UPLOADER", f"Получен upload URL, video_id={video_id}")
        
        # 2. Загружаем видео
        with open(file_path, "rb") as f:
            files = {"video_file": f}
            r = requests.post(upload_url, files=files, timeout=60)
        
        if r.status_code != 200:
            debug_log("VK_UPLOADER", f"Ошибка загрузки: {r.status_code}", "ERROR")
            return False, f"Ошибка HTTP {r.status_code}"
        
        debug_log("VK_UPLOADER", "Видео загружено, сохраняем...")
        
        # 3. Сохраняем видео
        save_params = {
            "access_token": vk_token,
            "v": "5.199",
            "video_id": video_id,
            "owner_id": owner_id_resp
        }
        r = requests.get("https://api.vk.com/method/video.save", params=save_params, timeout=30)
        data = r.json()
        
        if "error" in data:
            debug_log("VK_UPLOADER", f"Ошибка при сохранении: {data['error']['error_msg']}", "ERROR")
            return False, data["error"]["error_msg"]
        
        debug_log("VK_UPLOADER", "✅ Видео успешно загружено через VK API")
        return True, f"video{owner_id_resp}_{video_id}"
        
    except Exception as e:
        debug_log("VK_UPLOADER", f"Исключение: {e}", "ERROR")
        return False, str(e)
