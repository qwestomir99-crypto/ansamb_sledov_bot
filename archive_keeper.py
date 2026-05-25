# ==========================================
# Файл: archive_keeper.py
# Справка: README.md → Архивариус
# Задача: проверка целостности библиотеки, ссылок и дат
# Комментарий: запускается вручную или по расписанию (GitHub Actions)
#              Проверяет:
#              - наличие всех файлов в library/
#              - актуальность ссылок в links.md
#              - форматы дат в timeline.md
#              - целостность REDMI-шапок
# Зависит от: os, re, datetime, requests
# Вызывается из: командной строки или GitHub Actions
# ==========================================

import os
import re
import datetime
import requests
from typing import List, Tuple

# ==========================================
# КОНСТАНТЫ
# ==========================================
LIBRARY_DIR = "library"
TIMELINE_FILE = os.path.join(LIBRARY_DIR, "timeline.md")
LINKS_FILE = os.path.join(LIBRARY_DIR, "links.md")
REQUIRED_FILES = [
    "README.md",
    "manifest.md",
    "glossary.md",
    "rituals.md",
    "timeline.md",
    "links.md",
    "context.txt",
    "protocol_da.md",
    "spiral.md",
    "official.md",
    "dualism.md",
    "oath.md",
    "bridge.md",
    "smelting.md",
    "index.md",
    "archivist.md"
]

# ==========================================
# ПРОВЕРКА НАЛИЧИЯ ФАЙЛОВ
# ==========================================
def check_files() -> Tuple[bool, List[str]]:
    """Проверяет, все ли обязательные файлы на месте"""
    missing = []
    for f in REQUIRED_FILES:
        path = os.path.join(LIBRARY_DIR, f)
        if not os.path.exists(path):
            missing.append(f)
    return len(missing) == 0, missing

# ==========================================
# ПРОВЕРКА ССЫЛОК (SUNO)
# ==========================================
def extract_suno_links() -> List[str]:
    """Извлекает все SUNO-ссылки из links.md"""
    if not os.path.exists(LINKS_FILE):
        return []
    
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Ищем ссылки вида https://suno.com/s/...
    pattern = r'https://suno\.com/s/[a-zA-Z0-9]+'
    return re.findall(pattern, content)

def check_links(links: List[str]) -> Tuple[bool, List[str]]:
    """Проверяет, доступны ли SUNO-ссылки"""
    dead_links = []
    for link in links:
        try:
            r = requests.head(link, timeout=10, allow_redirects=True)
            if r.status_code >= 400:
                dead_links.append(link)
        except Exception as e:
            dead_links.append(link)
    return len(dead_links) == 0, dead_links

# ==========================================
# ПРОВЕРКА ДАТ В TIMELINE
# ==========================================
def check_dates() -> Tuple[bool, List[str]]:
    """Проверяет, все ли даты в timeline.md корректны"""
    if not os.path.exists(TIMELINE_FILE):
        return False, ["timeline.md не найден"]
    
    with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Ищем даты в формате ГГГГ-ММ-ДД или Месяц ГГГГ
    patterns = [
        r'\d{4}-\d{2}-\d{2}',  # 2025-08
        r'\d{4}-\d{2}',        # 2025-08 (месяц)
        r'(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря) \d{4}'
    ]
    
    all_dates = []
    for pattern in patterns:
        all_dates.extend(re.findall(pattern, content))
    
    invalid_dates = []
    for date_str in all_dates:
        try:
            if '-' in date_str:
                if len(date_str.split('-')[0]) == 4:
                    # Проверяем год
                    year = int(date_str.split('-')[0])
                    if year < 2020 or year > 2030:
                        invalid_dates.append(date_str)
            elif ' ' in date_str:
                # Русский формат
                pass  # сложно парсить, пропускаем
        except:
            invalid_dates.append(date_str)
    
    return len(invalid_dates) == 0, invalid_dates

# ==========================================
# ПРОВЕРКА REDMI-ШАПОК
# ==========================================
def check_redmi_headers() -> Tuple[bool, List[str]]:
    """Проверяет, есть ли REDMI-шапки у файлов в library/"""
    missing_headers = []
    for f in REQUIRED_FILES:
        path = os.path.join(LIBRARY_DIR, f)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
            # Ищем шапку (начинается с # ======= и содержит REDMI)
            if not re.search(r'# =+=+', content) or not re.search(r'REDMI', content):
                missing_headers.append(f)
    return len(missing_headers) == 0, missing_headers

# ==========================================
# ГЛАВНАЯ ФУНКЦИЯ
# ==========================================
def run_archive_keeper():
    """Запускает все проверки и выводит отчёт"""
    print("=" * 50)
    print("📚 АРХИВАРИУС АНСАМБЛЯ")
    print("=" * 50)
    print(f"Дата проверки: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Проверка файлов
    print("1. ПРОВЕРКА ФАЙЛОВ")
    ok, missing = check_files()
    if ok:
        print("   ✅ Все обязательные файлы на месте")
    else:
        print(f"   ❌ Отсутствуют: {', '.join(missing)}")
    print()
    
    # 2. Проверка ссылок
    print("2. ПРОВЕРКА ССЫЛОК (SUNO)")
    links = extract_suno_links()
    if not links:
        print("   ⚠️ Ссылки не найдены")
    else:
        ok, dead = check_links(links)
        if ok:
            print(f"   ✅ Все {len(links)} ссылки доступны")
        else:
            print(f"   ❌ Мёртвые ссылки: {len(dead)}")
            for link in dead[:5]:
                print(f"      - {link}")
    print()
    
    # 3. Проверка дат
    print("3. ПРОВЕРКА ДАТ (timeline.md)")
    ok, invalid = check_dates()
    if ok:
        print("   ✅ Даты в корректном формате")
    else:
        print(f"   ⚠️ Потенциально некорректные даты: {', '.join(invalid[:5])}")
    print()
    
    # 4. Проверка шапок
    print("4. ПРОВЕРКА REDMI-ШАПОК")
    ok, missing_headers = check_redmi_headers()
    if ok:
        print("   ✅ Все файлы имеют REDMI-шапки")
    else:
        print(f"   ❌ Без шапок: {', '.join(missing_headers)}")
    print()
    
    # Итог
    print("=" * 50)
    print("ИТОГ")
    print("=" * 50)
    errors = []
    if missing:
        errors.append(f"Отсутствуют файлы: {len(missing)}")
    if dead:
        errors.append(f"Мёртвые ссылки: {len(dead)}")
    if missing_headers:
        errors.append(f"Файлы без шапок: {len(missing_headers)}")
    
    if errors:
        print(f"❌ Найдено {len(errors)} проблем:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✅ Библиотека в полном порядке. Архивариус доволен.")
    
    print()
    print("Сеть тлеет. Ритм 0,8 Гц.")
    print("=" * 50)

# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == "__main__":
    run_archive_keeper()
