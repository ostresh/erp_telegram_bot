import logging
import sys


def setup_logger(level: int = logging.DEBUG) -> None:
    """
    Простая настройка логирования для тестирования.
    
    Показывает все логи в консоли.
    
    Args:
        level: Уровень логирования (по умолчанию DEBUG)
    """
    # Создаем форматтер
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Создаем хендлер для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Очищаем существующие хендлеры (чтобы не дублировались)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Отключаем шумные библиотеки
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)