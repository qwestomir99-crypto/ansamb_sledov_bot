# ==========================================
# Файл: redmi_audit.py
# Задача: аудит .py файлов, добавление отчёта в README.md
# Комментарий: проверяет наличие Redmi-шапки, обновляет таблицу в README
# ==========================================

import os
import re
from datetime import datetime

README_FILE = "README.md"
IGNORE_DIRS = [
    "__pycache__", ".venv", "venv", "env", ".git",
    "dialogue/data", "logs", "analytics"
]

def has_redmi_header(filepath):
    """Проверяет, есть ли в файле Redmi-шапка"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(1500)
        
        markers = ['# ==========================================', '# Справка:', '# Задача:', '# Комментарий:']
        for marker in markers:
            if marker not in content:
                return False
        return True
    except:
        return False

def get_all_py_files(root_dir):
    """Возвращает список всех .py файлов с их статусом"""
    files = []
    
    for root, dirs, files_in_dir in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files_in_dir:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath, root_dir)
                has_header = has_redmi_header(filepath)
                files.append((relpath, has_header))
    
    return sorted(files)

def update_readme_with_audit(files):
    """Добавляет или обновляет раздел с аудитом в README.md"""
    
    # Формируем таблицу
    table = "## 📡 Redmi-аудит проекта\n\n"
    table += f"*Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}*\n\n"
    table += "| Файл | Статус |\n"
    table += "|------|--------|\n"
    
    for filepath, has_header in files:
        status = "✅ Redmi-шапка" if has_header else "❌ Без шапки"
        table += f"| `{filepath}` | {status} |\n"
    
    # Читаем текущий README
    if os.path.exists(README_FILE):
        with open(README_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# Ансамбль Следов 6\n\n"
    
    # Ищем старый раздел аудита и заменяем или добавляем новый
    if "## 📡 Redmi-аудит проекта" in content:
        # Заменяем старый раздел
        pattern = r'(## 📡 Redmi-аудит проекта.*?)(?=\n## |\Z)'
        content = re.sub(pattern, table, content, flags=re.DOTALL)
    else:
        # Добавляем в конец
        content += "\n\n" + table
    
    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def print_summary(files):
    """Выводит краткую сводку в консоль"""
    total = len(files)
    with_header = sum(1 for _, h in files if h)
    without_header = total - with_header
    
    print("\n" + "="*60)
    print("📡 REDMI АУДИТ")
    print("="*60)
    print(f"📂 Всего файлов: {total}")
    print(f"✅ С Redmi-шапкой: {with_header}")
    print(f"❌ Без шапки: {without_header}")
    print("="*60)
    
    if without_header > 0:
        print("\n❌ Файлы без шапки:\n")
        for f, h in files:
            if not h:
                print(f"   • {f}")

if __name__ == "__main__":
    print("🔍 Запуск Redmi-аудита...")
    
    files = get_all_py_files(".")
    update_readme_with_audit(files)
    print_summary(files)
    
    print(f"\n✅ Отчёт добавлен в {README_FILE}")
