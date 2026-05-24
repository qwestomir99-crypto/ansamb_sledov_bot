# ==========================================
# Файл: dialogue/color_logger.py
# Справка: README.md → Отладка / Логирование
# Задача: настройка цветного вывода логов в консоль (debug, info, warning, error)
# Комментарий: используется для удобного чтения логов при локальной отладке и на Render
# Зависит от: logging, colorlog
# Вызывается из: debug_utils.py (или напрямую в модулях при отладке)
# ==========================================

import logging
import colorlog

def setup_logger():
    """Настраивает цветной логгер для консоли"""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Удаляем старые обработчики, если есть
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    # Цветной формат
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s[%(levelname)s] %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Создаём глобальный логгер
logger = setup_logger()

# Пример использования:
# logger.debug("Отладочное сообщение")
# logger.info("Информация")
# logger.warning("Предупреждение")
# logger.error("Ошибка")
