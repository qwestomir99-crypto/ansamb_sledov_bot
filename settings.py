# ==========================================
# Файл: settings.py
# Задача: глобальные настройки бота
# ==========================================

# -------------------- ОСНОВНЫЕ МОДУЛИ --------------------
ENABLE_VK_READER = True
ENABLE_JOURNALIST = True
ENABLE_QUOTES = True
ENABLE_SCHEDULER = True
ENABLE_PUBLISHER = True
ENABLE_AUTOPOSTER = True
ENABLE_CALLBACKS = True
ENABLE_ALISA = False

# -------------------- YOUTUBЕ АВТОПОСТИНГ --------------------
YOUTUBE_CHECK_INTERVAL = 60

# -------------------- ОТЛАДКА --------------------
DEBUG_MODE = True
DEBUG_MODULES = ["AUTOPOSTER", "VK_READER", "QUOTES", "PHOTO_READER", "PUBLISHER"]
DEBUG_IMPORTS = True
DEBUG_THREADS = True

# -------------------- НАСТРОЙКИ ПОЛЛИНГА --------------------
SKIP_PENDING_UPDATES = True
POLLING_DELAY = 2
POLLING_TIMEOUT = 60
LONG_POLLING_TIMEOUT = 60
