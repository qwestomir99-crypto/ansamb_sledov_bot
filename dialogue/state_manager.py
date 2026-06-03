# ==========================================
# Файл: dialogue/state_manager.py
# Справка: README.md → Управление состояниями
# Задача: централизованное хранение состояний пользователей
# Комментарий: вынесено из message_dispatcher для предотвращения циклических импортов
#              Используется в message_dispatcher, admin_commands, callbacks
# Зависит от: нет (чистый модуль)
# Вызывается из: message_dispatcher.py, admin_commands.py, callbacks/*.py
# ==========================================

# ==========================================
# ГЛОБАЛЬНЫЕ СЛОВАРИ ДЛЯ СОСТОЯНИЙ
# ==========================================

# Состояния пользователей
# Возможные значения:
#   - "waiting_dialog"       — диалог с агентом
#   - "waiting_quote_text"   — добавление цитаты (текст)
#   - "waiting_quote_interval" — установка интервала цитат
#   - "waiting_simple_post"  — добавление поста (текст + медиа)
user_states = {}

# Черновики постов (временное хранилище при добавлении)
# Структура: {user_id: {"text": "...", "tags": [...]}}
post_drafts = {}

# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (опционально)
# ==========================================

def get_state(user_id):
    """Возвращает текущее состояние пользователя или None"""
    return user_states.get(user_id)

def set_state(user_id, state):
    """Устанавливает состояние пользователя"""
    if state is None:
        user_states.pop(user_id, None)
    else:
        user_states[user_id] = state

def clear_state(user_id):
    """Очищает состояние и черновик пользователя"""
    user_states.pop(user_id, None)
    post_drafts.pop(user_id, None)

def get_draft(user_id):
    """Возвращает черновик поста пользователя"""
    return post_drafts.get(user_id)

def set_draft(user_id, draft):
    """Устанавливает черновик поста пользователя"""
    post_drafts[user_id] = draft

# ==========================================
# ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ STATE_MANAGER ===")
    test_user = 123456
    set_state(test_user, "test_state")
    print(f"Состояние: {get_state(test_user)}")
    clear_state(test_user)
    print(f"После очистки: {get_state(test_user)}")
    print("✅ Модуль state_manager работает")
