# ==========================================
# Файл: dialogue/admin/auth.py
# Справка: README.md → Админка (авторизация)
# Задача: проверка прав, сессии, блокировки
# Комментарий: импортируется в admin_commands.py и callbacks.py
# ==========================================

import os
import time
from datetime import datetime

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0))

# Хранилище активных сессий админа
admin_sessions = {}
SESSION_TIMEOUT = 1800  # 30 минут

# Блокировка после 3 попыток
failed_attempts = {}
BLOCK_TIME = 3600  # 1 час
MAX_ATTEMPTS = 3

def is_blocked(user_id):
    if user_id in failed_attempts:
        attempts, block_until = failed_attempts[user_id]
        if time.time() < block_until:
            return True
        else:
            del failed_attempts[user_id]
    return False

def register_failed_attempt(user_id, bot):
    attempts, block_until = failed_attempts.get(user_id, (0, 0))
    attempts += 1
    
    if attempts >= MAX_ATTEMPTS:
        block_until = time.time() + BLOCK_TIME
        try:
            bot.send_message(
                ADMIN_USER_ID,
                f"⚠️ *Попытка взлома админки!*\n\n"
                f"User ID: `{user_id}`\n"
                f"Заблокирован на 1 час.\n"
                f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='Markdown'
            )
        except:
            pass
        print(f"[ADMIN] Блокировка user_id {user_id} на 1 час")
    
    failed_attempts[user_id] = (attempts, block_until)

def is_admin_authorized(user_id):
    if user_id != ADMIN_USER_ID:
        return False
    if user_id in admin_sessions:
        if time.time() - admin_sessions[user_id] < SESSION_TIMEOUT:
            return True
    return False

def authorize_admin(user_id, password):
    if user_id == ADMIN_USER_ID and password == ADMIN_PASSWORD:
        admin_sessions[user_id] = time.time()
        return True
    return False

def logout_admin(user_id):
    admin_sessions.pop(user_id, None)
