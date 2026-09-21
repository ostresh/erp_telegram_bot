from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.core.db.unit_of_work import UnitOfWork
from app.core.service.menu.service import MenuService
import logging

logger = logging.getLogger(__name__)

router = Router(name="start")

@router.message(Command("start"))
async def cmd_start(message: Message, uow: UnitOfWork):
    """Показывает главное меню при команде /start"""
    
    logger.info(f"User {message.from_user.id} started the bot")
    
    try:
        async with uow() as session:
            menu_service = MenuService(session)
            menu = await menu_service.get_menu('main')
            
            await message.answer(
                text = menu.text,
                reply_markup= menu.keyboard,
                parse_mode='HTML'
            )
    except Exception as e:
        logger.exception(f"Error in /start: {e}")
        await message.answer("❌ Ошибка при загрузке меню. Попробуйте позже.")