# ==========================================
# Файл: settings.py
# Задача: глобальные настройки бота, флаги включения/выключения модулей
# ==========================================

# Основные модули
ENABLE_VK_READER = True      # Чтение постов из VK
ENABLE_JOURNALIST = True     # Журналист (дайджест)
ENABLE_QUOTES = True         # Цитаты
ENABLE_SCHEDULER = True      # Планировщик (полуночный ритуал)
ENABLE_PUBLISHER = True      # Публикатор (посты из пула)
ENABLE_AUTOPOSTER = True    # Автопостинг (требует Telethon, отключён)
ENABLE_CALLBACKS = True      # Обработчики кнопок

# Режимы
ENABLE_ALISA = False         # Алиса (отключена, используем агента)

# Отладка
DEBUG_IMPORTS = True         # Выводить диагностику импортов
DEBUG_THREADS = True         # Выводить диагностику потоков
