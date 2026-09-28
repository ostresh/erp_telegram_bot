from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, ShowMode

from app.interfaces.bot.callbacks import ActionCB
from app.interfaces.bot.dialogs.actions.goods.change_selling_price.states import ChangeSellingPriceSG
from app.core.service.menu import MenuService
from app.core.db.unit_of_work import UnitOfWork

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(ActionCB.filter(F.action == 'change-selling-price'))
async def start_change_selling_price_dialog(callback: CallbackQuery, callback_data: ActionCB, dialog_manager: DialogManager, uow: UnitOfWork):
    await callback.answer()
    
    async with uow() as session:
        service = MenuService(session)
        menu_text = service.build_breadcrumbs_text_from_path(callback_data.path)
    
    logger.info(f'User {callback.message.from_user.id} start change-selling-price dialog')
    
    await dialog_manager.start(
        state=ChangeSellingPriceSG.game_input,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT,
        data={
            'menu_text' : menu_text,
            'path' : callback_data.path
        }
    )
