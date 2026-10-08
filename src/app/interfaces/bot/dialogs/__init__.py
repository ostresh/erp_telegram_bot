"""
Регистрация всех диалогов в проекте.
"""

from aiogram import Dispatcher

from .actions import ACTION_DIALOGS

ALL_DIALOGS = [
    *ACTION_DIALOGS
]

def register_dialogs(dp: Dispatcher) -> None:
    """Регистрирует все диалоги в диспетчере."""
    
    for dialog in ALL_DIALOGS:
        dp.include_router(dialog)