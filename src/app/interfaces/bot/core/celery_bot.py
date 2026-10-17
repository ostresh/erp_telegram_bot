# src/app/bot/celery_bot.py

"""
Синглтон бота для Celery задач.

В рамках одного Celery worker процесса существует
только один экземпляр Bot. Это экономит ресурсы
и обеспечивает стабильность соединений.
"""

from aiogram import Bot
from .factory import create_bot


_bot_instance: Bot | None = None

async def close_bot() -> None:
    """Закрывает сессию бота при остановке worker."""
    global _bot_instance
    
    if _bot_instance is not None:
        await _bot_instance.session.close()
        _bot_instance = None