# ==========================================
# Файл: utils.py
# Справка: README.md → Вспомогательные утилиты
# Задача: общие функции для работы с текстом, файлами, экранированием
# Комментарий: используется в разных модулях (bot.py, publisher_utils.py и др.)
# Зависит от: re, os
# Вызывается из: bot.py, publisher_utils.py, admin_commands.py
# ==========================================

import re
import os

def escape_markdown(text: str) -> str:
    """
    Экранирует спецсимволы для MarkdownV2 в Telegram.
    Список символов: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


def sanitize_filename(filename: str, max_length: int = 50) -> str:
    """
    Очищает имя файла от проблемных символов.
    Заменяет нелатинские буквы, пробелы, скобки и т.д. на '_'.
    """
    name, ext = os.path.splitext(filename)
    clean_name = re.sub(r'[^a-zA-Z0-9а-яА-Я._-]', '_', name)
    if len(clean_name) > max_length:
        clean_name = clean_name[:max_length]
    return f"{clean_name}{ext.lower()}"


def safe_send_audio(bot, chat_id, file_path: str, caption: str = None):
    """
    Безопасная отправка аудио: экранирует caption и открывает файл.
    """
    if not os.path.exists(file_path):
        print(f"[UTILS] Файл не найден: {file_path}")
        return False
    
    safe_caption = escape_markdown(caption) if caption else None
    
    with open(file_path, 'rb') as f:
        bot.send_audio(
            chat_id,
            audio=f,
            caption=safe_caption,
            parse_mode='MarkdownV2' if safe_caption else None
        )
    return True


def safe_send_video(bot, chat_id, file_path: str, caption: str = None):
    """
    Безопасная отправка видео: экранирует caption и открывает файл.
    """
    if not os.path.exists(file_path):
        print(f"[UTILS] Файл не найден: {file_path}")
        return False
    
    safe_caption = escape_markdown(caption) if caption else None
    
    with open(file_path, 'rb') as f:
        bot.send_video(
            chat_id,
            video=f,
            caption=safe_caption,
            parse_mode='MarkdownV2' if safe_caption else None
        )
    return True
