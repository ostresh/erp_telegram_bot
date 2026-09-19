from aiogram import Router
from aiogram.types import CallbackQuery
from app.bot.callbacks.menu import MenuCB
from app.db.unit_of_work import UnitOfWork
from app.service.menu.service import MenuService
import logging

logger = logging.getLogger(__name__)
router = Router(name="navigation")


@router.callback_query(MenuCB.filter())
async def menu_navigation_handler(
    callback: CallbackQuery,
    callback_data: MenuCB,
    uow: UnitOfWork,
):
    """
    Универсальный обработчик навигации по меню.
    
    Если title='back' — возвращает родительское меню,
    иначе открывает запрошенное меню.
    """
    
    await callback.answer()
    
    try:
        async with uow() as session:
            menu_service = MenuService(session)
            
            if callback_data.title == 'back':
                menu = await menu_service.get_back_menu(callback_data.path)
            else:
                menu = await menu_service.get_menu(callback_data.path)
                
            await callback.message.edit_text(
                text=menu.text,
                reply_markup=menu.keyboard,
                parse_mode='HTML',
            )
            
            logger.info(
                f"User {callback.from_user.id} navigated to {menu.path}"
            )
            
    except ValueError as e:
        logger.warning(f"Invalid menu path: {e}")
        await callback.answer("❌ Меню не найдено", show_alert=True)
        
    except Exception as e:
        logger.exception(f"Error in menu navigation: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)