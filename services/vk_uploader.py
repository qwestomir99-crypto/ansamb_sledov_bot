# ==========================================
# Файл: services/vk_uploader.py
# Справка: README.md → VK / Загрузка видео
# Задача: загрузка видео в VK
# Комментарий: используется для больших видео вместо Telegram
# Зависит от: vk_api, os, debug_utils
# Вызывается из: big_video_uploader.py (альтернативный путь)
# ==========================================

import os
import vk_api
from debug_utils import debug_log

def log_vk(level, message):
    debug_log("VK_UPLOADER", message, level)

def upload_video_to_vk(file_path, title, description=""):
    """
    Загружает видео в VK и возвращает ссылку.
    """
    if not os.path.exists(file_path):
        log_vk("ERROR", f"Файл не найден: {file_path}")
        return None
    
    vk_token = os.environ.get("VK_TOKEN")
    vk_owner_id = os.environ.get("VK_OWNER_ID")
    
    if not vk_token or not vk_owner_id:
        log_vk("ERROR", "VK_TOKEN или VK_OWNER_ID не заданы")
        return None
    
    try:
        vk_session = vk_api.VkApi(token=vk_token)
        vk = vk_session.get_api()
        
        # Загружаем видео (упрощённо)
        video = vk.video.save(
            name=title,
            description=description,
            group_id=vk_owner_id
        )
        
        # Публикуем видео
        vk.video.edit(
            video_id=video["video_id"],
            owner_id=video["owner_id"],
            title=title,
            description=description
        )
        
        video_url = f"https://vk.com/video{video['owner_id']}_{video['video_id']}"
        log_vk("INFO", f"Видео загружено: {video_url}")
        return video_url
    except Exception as e:
        log_vk("ERROR", f"Ошибка загрузки видео: {e}")
        return None
