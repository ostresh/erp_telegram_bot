from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode, ShowMode

from app.bot.callbacks import ActionCB
from app.bot.dialogs.actions.goods.buy_goods.states import BuyGoodsSG
from app.service.menu import MenuService
from app.db.unit_of_work import UnitOfWork

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(ActionCB.filter(F.action == 'buy-goods'))
async def start_buy_goods_dialog(callback: CallbackQuery, callback_data: ActionCB, dialog_manager: DialogManager, uow: UnitOfWork):
    await callback.answer()
    
    async with uow() as session:
        service = MenuService(session)
        menu_text = service.build_breadcrumbs_text_from_path(callback_data.path)
    
    logger.info(f'User {callback.message.from_user.id} start buy-goods dialog')
    
    await dialog_manager.start(
        state=BuyGoodsSG.type_game,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT,
        data={
            'menu_text' : menu_text,
            'path' : callback_data.path
        }
    )
