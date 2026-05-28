# ==========================================
# Файл: services/internal_line.py
# Справка: README.md → Внутренняя линия
# Задача: читает library/links.md и строит гибридный (SQL + файлы) индекс артефактов
# Комментарий: используется ботом для поиска и связей артефактов
# Зависит от: os, re, json, services.supabase_client
# Вызывается из: bot.py (при старте), track_commands.py (при запросах)
# ==========================================

import os
import re
import json
from services.supabase_client import db_insert, db_select

LINKS_FILE = "library/links.md"
ARTIFACTS_TABLE = "artifacts"

def log_line(level, message):
    debug_log("INTERNAL_LINE", message, level)

# ==========================================
# 1. ПАРСИНГ library/links.md
# ==========================================
def parse_links_file():
    """Читает library/links.md и возвращает список артефактов"""
    if not os.path.exists(LINKS_FILE):
        log_line("WARNING", f"{LINKS_FILE} не найден")
        return []
    
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    artifacts = []
    current_section = None
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Определяем секцию
        if line.startswith('## '):
            current_section = line.replace('## ', '').strip()
            continue
        
        # Парсим строки артефактов
        if line.startswith('- '):
            parts = line[2:].split(':', 1)
            if len(parts) == 2:
                name = parts[0].strip()
                value = parts[1].strip().strip('[]')
                artifacts.append({
                    "name": name,
                    "url": value,
                    "section": current_section,
                    "type": "link"
                })
    
    log_line("INFO", f"Загружено {len(artifacts)} артефактов из {LINKS_FILE}")
    return artifacts

# ==========================================
# 2. ЗАГРУЗКА В SQL
# ==========================================
def load_artifacts_to_sql(artifacts):
    """Загружает артефакты в таблицу artifacts"""
    for artifact in artifacts:
        db_insert(ARTIFACTS_TABLE, {
            "name": artifact["name"],
            "url": artifact["url"],
            "section": artifact["section"],
            "type": artifact["type"]
        })
    log_line("INFO", f"Загружено {len(artifacts)} записей в SQL")

# ==========================================
# 3. ПОИСК АРТЕФАКТОВ
# ==========================================
def find_artifact(query, limit=5):
    """Ищет артефакт по имени через SQL (фоллбэк на файл)"""
    # Попытка через SQL
    result = db_select(ARTIFACTS_TABLE, limit=limit, filter_by={"name": query})
    if result:
        return result
    
    # Фоллбэк на файл
    artifacts = parse_links_file()
    matches = [a for a in artifacts if query.lower() in a["name"].lower()]
    return matches[:limit]

# ==========================================
# 4. ИНИЦИАЛИЗАЦИЯ
# ==========================================
def init_internal_line():
    """Запускается при старте бота"""
    artifacts = parse_links_file()
    if artifacts:
        load_artifacts_to_sql(artifacts)
    log_line("INFO", "Внутренняя линия инициализирована")

# ==========================================
# 5. ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ ВНУТРЕННЕЙ ЛИНИИ ===")
    init_internal_line()
    result = find_artifact("Мы просто не спрашивали разрешения")
    print(f"Найдено: {result}")
