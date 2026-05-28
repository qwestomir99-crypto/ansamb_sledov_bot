# ==========================================
# Файл: services/tracking.py
# Справка: README.md → Трекер событий
# Задача: ловит команды #трек, #картина, #сценарий и возвращает ссылки
# Комментарий: использует internal_line для поиска
# Зависит от: internal_line, debug_utils
# Вызывается из: bot.py (обработчик команд)
# ==========================================

from debug_utils import debug_log
from services.internal_line import find_artifact

def log_track(level, message):
    debug_log("TRACKING", message, level)

# ==========================================
# 1. ОБРАБОТЧИКИ КОМАНД
# ==========================================
def handle_track_command(command, query):
    """
    Обрабатывает команды #трек, #картина, #сценарий.
    Возвращает ссылку на артефакт или None.
    """
    if not query:
        log_track("WARNING", f"Пустой запрос для {command}")
        return None
    
    artifacts = find_artifact(query)
    if not artifacts:
        log_track("INFO", f"Артефакт '{query}' не найден")
        return None
    
    # Если нашли несколько — берём первый
    return artifacts[0].get("url")

# ==========================================
# 2. КОМАНДЫ ДЛЯ БОТА
# ==========================================
def track_track(query):
    return handle_track_command("#трек", query)

def track_picture(query):
    return handle_track_command("#картина", query)

def track_blueprint(query):
    return handle_track_command("#сценарий", query)

# ==========================================
# 3. ТЕСТ
# ==========================================
if __name__ == "__main__":
    print("=== ТЕСТ ТРЕКЕРА ===")
    url = track_track("Мы просто не спрашивали разрешения")
    print(f"Результат: {url}")
