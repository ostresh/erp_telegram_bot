import logging
import sys
from colorlog import ColoredFormatter


def setup_logger(level: int = logging.DEBUG) -> None:
    """
    Настройка цветного логирования.
    
    Обычные уровни (DEBUG, INFO) - обычным шрифтом, приглушенные цвета.
    Ошибки (WARNING, ERROR, CRITICAL) - жирным шрифтом, яркие цвета.
    """
    
    # Цветной форматтер
    # %(log_color)s стоит в начале и применяется ко ВСЕЙ строке,
    # так как нет %(reset)s до конца строки
    formatter = ColoredFormatter(
        fmt=(
            '%(log_color)s%(asctime)s | %(levelname)-8s | '
            '%(name)s | %(message)s'
        ),
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG': 'light_blue',       # Приглушенный синий
            'INFO': 'light_green',       # Приглушенный зеленый
            'WARNING': 'bold_yellow',         # Обычный жёлтый
            'ERROR': 'bold_red',         # ЖИРНЫЙ красный
            'CRITICAL': 'bold_red',      # ЖИРНЫЙ красный
        }
    )
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Отключаем шумные библиотеки
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)