"""
Регистрация всех диалогов в проекте.
"""

from aiogram import Dispatcher

from app.interfaces.bot.dialogs.test.hello_dialog import hello_dialog
from .actions import ACTION_DIALOGS

ALL_DIALOGS = [
    *ACTION_DIALOGS
]

def register_dialogs(dp: Dispatcher) -> None:
    """Регистрирует все диалоги в диспетчере."""
    dp.include_router(hello_dialog)
    
    for dialog in ALL_DIALOGS:
        dp.include_router(dialog)