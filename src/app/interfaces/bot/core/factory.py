"""
Фабрика создания экземпляров бота.

Используется в:
- main.py — для polling (получения сообщений)
- Celery worker — для отправки/удаления сообщений
- Тесты — для создания тестового бота
"""

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession

from config import config


def create_bot() -> Bot:
    """
    Создаёт экземпляр бота с настройками окружения.
    
    В production:
        - Без прокси
        - Обычные настройки
    
    В development:
        - С SOCKS5 прокси для обхода блокировок
        - Для работы из России
        
    Returns:
        Bot: Настроенный экземпляр бота
    """
    default_props = DefaultBotProperties(parse_mode=ParseMode.HTML)
    
    if config.is_production:
        return Bot(
            token=config.BOT_TOKEN,
            default=default_props,
        )
    
    # Development — с прокси
    session = AiohttpSession(
        proxy="socks5://127.0.0.1:3067",
        timeout=60.0,
    )
    
    return Bot(
        token=config.BOT_TOKEN,
        default=default_props,
        session=session,
    )