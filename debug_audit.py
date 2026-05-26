# ==========================================
# Файл: debug_audit.py
# Справка: README.md → Дебаггер / Аудит
# Задача: сканирование кода, проверка целостности, обновление индекса
# Комментарий: запускается вручную или по расписанию (GitHub Actions)
#              Проверяет:
#              - наличие REDMI-шапок
#              - корректность импортов
#              - целостность ссылок в библиотеке
#              - актуальность debug_index.json
# Зависит от: os, re, json, datetime, requests
# Вызывается из: командной строки, debug_utils.py, GitHub Actions
# ==========================================

import os
import re
import json
import datetime
import requests
from typing import List, Tuple, Dict

# ==========================================
# КОНСТАНТЫ
# ==========================================
LIBRARY_DIR = "library"
INDEX_FILE = "debug_index.json"
ERROR_LOG = "debug.log"
AUDIT_LOG = "logs/audit.log"

# Файлы и папки для проверки
PYTHON_DIRS = ["dialogue", "services", "."]
LIBRARY_FILES = [
    "README.md", "manifest.md", "glossary.md", "rituals.md",
    "timeline.md", "links.md", "context.txt", "protocol_da.md",
    "spiral.md", "official.md", "dualism.md", "oath.md",
    "bridge.md", "smelting.md", "index.md", "archivist.md",
    "midrash_spiral.md", "tree.md"
]

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def log_audit(message: str, level: str = "INFO"):
    """Записывает сообщение в лог аудита"""
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {level} | {message}\n")
    print(f"[AUDIT] {message}")

def load_index() -> Dict:
    """Загружает debug_index.json"""
    if not os.path.exists(INDEX_FILE):
        log_audit("debug_index.json не найден, создаю новый", "WARNING")
        return {"version": "1.0", "modules": {}, "connections": {}, "error_patterns": {}, "health_checks": {}}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_index(index: Dict):
    """Сохраняет debug_index.json"""
    index["last_updated"] = datetime.datetime.now().isoformat()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    log_audit("debug_index.json обновлён")

# ==========================================
# ПРОВЕРКА REDMI-ШАПОК
# ==========================================
def check_redmi_headers() -> Tuple[bool, List[str]]:
    """Проверяет наличие REDMI-шапок в файлах проекта"""
    missing = []
    for directory in PYTHON_DIRS:
        if not os.path.exists(directory):
            continue
        for root, dirs, files in os.walk(directory):
            # Исключаем лишние папки
            if "new_debugger" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Ищем шапку (начинается с # ======= и содержит REDMI)
                        if not re.search(r'# =+=+', content) or not re.search(r'REDMI', content):
                            missing.append(path)
    return len(missing) == 0, missing

# ==========================================
# ПРОВЕРКА БИБЛИОТЕКИ
# ==========================================
def check_library() -> Tuple[bool, List[str], List[str]]:
    """Проверяет наличие файлов и целостность ссылок в библиотеке"""
    missing_files = []
    broken_links = []
    
    # Проверка наличия файлов
    for f in LIBRARY_FILES:
        path = os.path.join(LIBRARY_DIR, f)
        if not os.path.exists(path):
            missing_files.append(f)
    
    # Проверка ссылок в links.md
    links_file = os.path.join(LIBRARY_DIR, "links.md")
    if os.path.exists(links_file):
        with open(links_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Ищем SUNO-ссылки
        suno_links = re.findall(r'https://suno\.com/s/[a-zA-Z0-9]+', content)
        for link in suno_links:
            try:
                r = requests.head(link, timeout=10, allow_redirects=True)
                if r.status_code >= 400:
                    broken_links.append(link)
            except:
                broken_links.append(link)
    
    return len(missing_files) == 0 and len(broken_links) == 0, missing_files, broken_links

# ==========================================
# ПРОВЕРКА ИМПОРТОВ (базовая)
# ==========================================
def check_imports() -> Tuple[bool, List[str]]:
    """Проверяет, что ключевые импорты в app.py работают"""
    issues = []
    app_file = "services/app.py"
    if os.path.exists(app_file):
        with open(app_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Проверяем, что blueprint'и зарегистрированы
        if "register_blueprint(web_api)" not in content:
            issues.append("web_api blueprint не зарегистрирован в app.py")
        if "register_blueprint(vk_api_bp)" not in content:
            issues.append("vk_api_bp blueprint не зарегистрирован в app.py")
        if "register_blueprint(tg_api_bp)" not in content:
            issues.append("tg_api_bp blueprint не зарегистрирован в app.py")
    
    return len(issues) == 0, issues

# ==========================================
# СБОР СТАТИСТИКИ ПО ЛОГАМ
# ==========================================
def analyze_logs() -> Dict:
    """Анализирует debug.log на предмет частоты ошибок"""
    if not os.path.exists(ERROR_LOG):
        return {"total_errors": 0, "top_errors": []}
    
    with open(ERROR_LOG, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    error_count = {}
    for line in lines:
        if "ERROR" in line:
            # Извлекаем тип ошибки
            match = re.search(r'\[(\w+)\].*ERROR', line)
            if match:
                module = match.group(1)
                error_count[module] = error_count.get(module, 0) + 1
    
    total = sum(error_count.values())
    top = sorted(error_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_errors": total,
        "top_errors": [{"module": k, "count": v} for k, v in top]
    }

# ==========================================
# ГЛАВНАЯ ФУНКЦИЯ
# ==========================================
def run_audit():
    """Запускает полную проверку и обновляет индекс"""
    log_audit("=" * 50)
    log_audit("НАЧАЛО АУДИТА")
    log_audit("=" * 50)
    
    results = {}
    
    # 1. Проверка REDMI-шапок
    log_audit("1. Проверка REDMI-шапок")
    ok, missing = check_redmi_headers()
    results["redmi_headers"] = {"ok": ok, "missing": missing}
    if ok:
        log_audit("   ✅ Все файлы имеют REDMI-шапки")
    else:
        log_audit(f"   ❌ Нет шапок: {len(missing)} файлов")
    
    # 2. Проверка библиотеки
    log_audit("2. Проверка библиотеки")
    ok, missing_files, broken_links = check_library()
    results["library"] = {"ok": ok, "missing_files": missing_files, "broken_links": broken_links}
    if ok:
        log_audit("   ✅ Библиотека в порядке")
    else:
        if missing_files:
            log_audit(f"   ❌ Отсутствуют файлы: {', '.join(missing_files)}")
        if broken_links:
            log_audit(f"   ❌ Битые ссылки: {len(broken_links)}")
    
    # 3. Проверка импортов
    log_audit("3. Проверка импортов (app.py)")
    ok, issues = check_imports()
    results["imports"] = {"ok": ok, "issues": issues}
    if ok:
        log_audit("   ✅ Все импорты корректны")
    else:
        for issue in issues:
            log_audit(f"   ❌ {issue}")
    
    # 4. Анализ логов
    log_audit("4. Анализ debug.log")
    stats = analyze_logs()
    results["logs"] = stats
    log_audit(f"   📊 Всего ошибок: {stats['total_errors']}")
    if stats['top_errors']:
        log_audit(f"   📊 Топ ошибок: {stats['top_errors'][0]['module']} — {stats['top_errors'][0]['count']} раз")
    
    # 5. Обновляем индекс
    log_audit("5. Обновление debug_index.json")
    index = load_index()
    index["last_audit"] = datetime.datetime.now().isoformat()
    index["audit_results"] = results
    save_index(index)
    
    # Итог
    log_audit("=" * 50)
    log_audit("ИТОГ АУДИТА")
    log_audit("=" * 50)
    total_issues = len(missing) + len(missing_files) + len(broken_links) + len(issues)
    if total_issues == 0:
        log_audit("✅ АУДИТ ПРОЙДЕН. ВСЁ В ПОРЯДКЕ.")
    else:
        log_audit(f"⚠️ НАЙДЕНО ПРОБЛЕМ: {total_issues}")
    
    log_audit("Сеть тлеет. Ритм 0,8 Гц.")
    log_audit("=" * 50)
    
    return results

# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == "__main__":
    run_audit()
