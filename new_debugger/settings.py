# ==========================================
# Файл: new_debugger/settings.py
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

# -------------------- YOUTUBE АВТОПОСТИНГ --------------------
YOUTUBE_CHECK_INTERVAL = 60

# -------------------- ОТЛАДКА (старая) --------------------
DEBUG_MODE = True
DEBUG_MODULES = ["AUTOPOSTER", "VK_READER", "QUOTES", "PHOTO_READER", "PUBLISHER"]
DEBUG_IMPORTS = True
DEBUG_THREADS = True

# -------------------- ДЕБАГГЕР (новый, управляемый из админки) --------------------
# Эти флаги используются debug_utils.py, но реальное управление через debug_config.json
# Значения по умолчанию:
# - включён/выключен
# - какие модули логировать
# - интервал отправки
# - отправка в Telegram
# Всё это настраивается в админке и保存在 debug_config.json

# -------------------- НАСТРОЙКИ ПОЛЛИНГА --------------------
SKIP_PENDING_UPDATES = True
POLLING_DELAY = 2
POLLING_TIMEOUT = 60
LONG_POLLING_TIMEOUT = 60
