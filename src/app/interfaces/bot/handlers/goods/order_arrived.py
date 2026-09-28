from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, ShowMode

from app.interfaces.bot.callbacks import ActionCB
from app.interfaces.bot.dialogs.actions.goods.order_arrived.states import OrderArrivedSG
from app.core.service.menu import MenuService
from app.core.db.unit_of_work import UnitOfWork

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(ActionCB.filter(F.action == 'order-arrived'))
async def start_buy_goods_dialog(callback: CallbackQuery, callback_data: ActionCB, dialog_manager: DialogManager, uow: UnitOfWork):
    await callback.answer()
    
    async with uow() as session:
        service = MenuService(session)
        menu_text = service.build_breadcrumbs_text_from_path(callback_data.path)
    
    logger.info(f'User {callback.message.from_user.id} start order-arrived dialog')
    
    await dialog_manager.start(
        state=OrderArrivedSG.select_order_recipient,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT,
        data={
            'menu_text' : menu_text,
            'path' : callback_data.path
        }
    )
