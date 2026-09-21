"""
Хендлер запуска тестового диалога hello → world.

Запускается командой /hello.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, ShowMode

from app.interfaces.bot.dialogs.test.hello_dialog import HelloSG
import logging

logger = logging.getLogger(__name__)
router = Router(name="hello")


@router.message(Command("hello"))
async def cmd_hello(message: Message, dialog_manager: DialogManager):
    """Запускает тестовый диалог"""
    logger.info(f"User {message.from_user.id} started hello dialog")
    
    await dialog_manager.start(
        state=HelloSG.main,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT,
    )