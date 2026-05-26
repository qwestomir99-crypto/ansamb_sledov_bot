# ==========================================
# Файл: dialogue/agent_reader.py
# Справка: README.md → Агент / Чтение из сети
# Задача: дать агенту возможность читать контент из сети и сохранять линки
# Комментарий: сохраняет только метаданные, не контент (экономия места)
#              Работает в связке с library/links.md
# Зависит от: requests, json, os, datetime, debug_utils
# Вызывается из: agent.py (в свободном режиме)
# ==========================================

import os
import json
import requests
from datetime import datetime
from debug_utils import debug_log

# ==========================================
# КОНФИГУРАЦИЯ
# ==========================================
LINKS_FILE = "library/links.md"

def log_reader(level, message):
    debug_log("AGENT_READER", message, level)

# ==========================================
# ИЗВЛЕЧЕНИЕ МЕТАДАННЫХ ИЗ ССЫЛКИ
# ==========================================
def extract_metadata(url):
    """
    Извлекает базовые метаданные из URL.
    Возвращает словарь с title, description, author, type.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        
        # Парсинг HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        
        title = soup.title.string.strip() if soup.title else "Без названия"
        description = ""
        author = ""
        
        # Ищем мета-теги
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '').strip()
        
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author:
            author = meta_author.get('content', '').strip()
        
        # Определяем тип контента
        content_type = "unknown"
        if "youtube.com" in url or "youtu.be" in url:
            content_type = "video"
        elif "suno.com" in url:
            content_type = "audio"
        elif "github.com" in url:
            content_type = "code"
        elif "vk.com" in url or "vkontakte.ru" in url:
            content_type = "social"
        elif "t.me" in url:
            content_type = "telegram"
        
        return {
            "url": url,
            "title": title[:200],
            "description": description[:300],
            "author": author[:100],
            "type": content_type,
            "timestamp": datetime.now().isoformat()
        }
    except ImportError:
        log_reader("ERROR", "Не установлен BeautifulSoup, используется fallback")
        # Fallback: только URL и базовое определение
        return {
            "url": url,
            "title": "Ссылка",
            "description": "Извлечение без BeautifulSoup",
            "author": "",
            "type": "unknown",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        log_reader("ERROR", f"Ошибка извлечения метаданных: {e}")
        return None

# ==========================================
# СОХРАНЕНИЕ ССЫЛКИ В БИБЛИОТЕКУ
# ==========================================
def save_link_to_library(metadata, tags=None):
    """
    Сохраняет ссылку в library/links.md в структурированном виде.
    """
    if not metadata:
        return False
    
    os.makedirs(os.path.dirname(LINKS_FILE), exist_ok=True)
    
    # Форматируем запись
    entry = f"\n\n## {metadata.get('title', 'Без названия')}\n"
    entry += f"- **URL:** [{metadata.get('url', '#')}]({metadata.get('url', '#')})\n"
    if metadata.get('description'):
        entry += f"- **Описание:** {metadata['description']}\n"
    if metadata.get('author'):
        entry += f"- **Автор:** {metadata['author']}\n"
    if metadata.get('type'):
        entry += f"- **Тип:** {metadata['type']}\n"
    if tags:
        entry += f"- **Теги:** {', '.join(tags)}\n"
    entry += f"- **Добавлено:** {metadata.get('timestamp', datetime.now().isoformat())}\n"
    entry += f"\n---"
    
    try:
        with open(LINKS_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        log_reader("INFO", f"Ссылка сохранена: {metadata.get('title', 'Без названия')}")
        return True
    except Exception as e:
        log_reader("ERROR", f"Ошибка сохранения: {e}")
        return False

# ==========================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==========================================
def agent_read_url(url, tags=None):
    """Основная функция: прочитать ссылку и сохранить в библиотеку"""
    log_reader("INFO", f"Агент читает: {url}")
    metadata = extract_metadata(url)
    if metadata:
        return save_link_to_library(metadata, tags)
    return False

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ AGENT_READER ===")
    test_url = "https://github.com/qwestomir99-crypto/ansamb_sledov_bot"
    success = agent_read_url(test_url, tags=["проект", "код"])
    print(f"Результат: {'✅' if success else '❌'}")
