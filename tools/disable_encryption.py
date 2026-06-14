#!/usr/bin/env python3
# ==========================================
# Файл: tools/disable_encryption.py
# Задача: временно отключить шифрование и переключиться на .env
# ==========================================

import os
import shutil

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
backup_path = os.path.join(project_root, 'data', 'secrets_backup.json')

print("🔧 Отключаю шифрование и переключаюсь на .env...")

# 1. Бэкапим базу
if os.path.exists(os.path.join(project_root, 'data', 'ansambl.db')):
    shutil.copy(
        os.path.join(project_root, 'data', 'ansambl.db'),
        os.path.join(project_root, 'data', 'ansambl.db.bak')
    )
    print("✅ База забэкаплена: data/ansambl.db.bak")

# 2. Переключаем secrets_manager.py на заглушку
secrets_path = os.path.join(project_root, 'services', 'secrets_manager.py')
with open(secrets_path, 'w') as f:
    f.write("""
# ==========================================
# ВРЕМЕННАЯ ЗАГЛУШКА (шифрование отключено)
# ==========================================
import os

def get_secret(key, default=None):
    return os.getenv(key, default)

def get_all_secrets():
    return {}
""")
print("✅ secrets_manager.py переключён на .env")

# 3. Создаём .env, если его нет
if not os.path.exists(env_path):
    print("⚠️ .env не найден. Создаю пустой.")
    with open(env_path, 'w') as f:
        f.write("")
    print("✅ .env создан")

print("🎉 Готово. Бот теперь читает секреты из .env")
print("Запустите бота и проверьте работу.")
