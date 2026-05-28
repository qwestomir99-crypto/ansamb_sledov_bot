# ==========================================
# Файл: services/big_video_uploader.py
# Справка: README.md → Большие видео
# Задача: отправка больших видео через VK (обход API_ID и API_HASH)
# Комментарий: использует VK как промежуточное хранилище
# Зависит от: vk_uploader, debug_utils
# Вызывается из: bot.py (команда /bigvideo)
# ==========================================

import os
import tempfile
from services.vk_uploader import upload_video_to_vk
from debug_utils import debug_log

def log_bv(level, message):
    debug_log("BIG_VIDEO", message, level)

def send_big_video(file_path, caption=""):
    """
    Отправляет большое видео через VK (обход Telegram).
    """
    if not os.path.exists(file_path):
        log_bv("ERROR", f"Файл не найден: {file_path}")
        return False
    
    video_url = upload_video_to_vk(file_path, "Большое видео", caption)
    if not video_url:
        log_bv("ERROR", "Не удалось загрузить видео в VK")
        return False
    
    # Отправляем ссылку в Telegram
    bot.send_message(
        ADMIN_USER_ID,
        f"🎬 *Большое видео загружено в VK:*\n\n{video_url}\n\n{caption}",
        parse_mode='Markdown'
    )
    log_bv("INFO", f"Отправлена ссылка на видео: {video_url}")
    return True
