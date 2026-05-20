# ==========================================
# Файл: services/web.py
# Справка: README.md → Web-утилиты
# Задача: вспомогательные функции для работы с веб-запросами
# Комментарий: используется для скачивания файлов по URL
# Зависит от: requests, os
# Вызывается из: admin_commands.py, publisher.py
# ==========================================

import requests
import os
import tempfile

def download_file_by_url(url, timeout=30):
    """
    Скачивает файл по URL и сохраняет во временный файл.
    Возвращает путь к временному файлу или None при ошибке.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Определяем расширение из URL или Content-Type
        ext = url.split('.')[-1].split('?')[0]
        if len(ext) > 5 or not ext:
            ext = 'jpg'
        
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}')
        tmp.write(response.content)
        tmp.close()
        
        return tmp.name
    except Exception as e:
        print(f"[WEB] Ошибка скачивания: {e}")
        return None

def file_exists(file_path):
    """Проверяет существование файла"""
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

def delete_temp_file(file_path):
    """Удаляет временный файл (если существует)"""
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            return True
    except Exception as e:
        print(f"[WEB] Ошибка удаления файла: {e}")
    return False
