# ==========================================
# Файл: big_video_uploader.py
# Справка: README.md → Автопостинг / Большие видео
# Задача: загрузка видео (>50 МБ) в VK через vk_api
# Комментарий: переписано с telethon на vk_api, чтобы избежать 409
# Зависит от: vk_api, os, requests
# Вызывается из: bot.py (команда /bigvideo), services/autoposter.py
# ==========================================

import os
import vk_api
from vk_api.upload import VkUpload
from debug_utils import debug_log

VK_TOKEN = os.environ.get("VK_TOKEN")
VK_OWNER_ID = int(os.environ.get("VK_OWNER_ID", 0))

def log_bv(level, message):
    debug_log("BIG_VIDEO", message, level)

def upload_video_to_vk(file_path: str, caption: str = ""):
    """
    Загружает видео в VK.
    Возвращает ссылку на видео или None в случае ошибки.
    """
    if not VK_TOKEN:
        log_bv("ERROR", "VK_TOKEN не задан")
        return None
    
    if not os.path.exists(file_path):
        log_bv("ERROR", f"Файл {file_path} не найден")
        return None
    
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        upload = VkUpload(vk_session)
        
        # Загружаем видео
        log_bv("INFO", f"Загрузка видео {file_path} в VK...")
        video_data = upload.video(file_path)
        
        # Получаем ссылку на видео
        video_id = video_data.get('video_id')
        owner_id = video_data.get('owner_id')
        video_url = f"https://vk.com/video{owner_id}_{video_id}"
        
        log_bv("INFO", f"Видео загружено: {video_url}")
        
        # Если есть подпись — добавляем её к посту
        if caption:
            from services.vk_api import api_vk_comment
            post_data = {
                "post_id": video_id,
                "text": caption
            }
            # Здесь можно вызвать API для постинга или просто вернуть ссылку
        
        return video_url
    except Exception as e:
        log_bv("ERROR", f"Ошибка загрузки видео: {e}")
        return None

def send_big_video(file_path: str, caption: str = ""):
    """
    Отправляет видео в VK (обёртка для upload_video_to_vk).
    """
    url = upload_video_to_vk(file_path, caption)
    if url:
        log_bv("INFO", f"Успешно: {url}")
        return True
    else:
        log_bv("ERROR", "Ошибка отправки видео")
        return False

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ BIG_VIDEO ===")
    print("VK_TOKEN:", "есть" if VK_TOKEN else "нет")
    print("VK_OWNER_ID:", VK_OWNER_ID)
    print("Для теста передайте файл через командную строку.")
