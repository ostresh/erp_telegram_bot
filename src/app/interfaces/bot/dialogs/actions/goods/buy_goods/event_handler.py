from typing import ClassVar

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput

from app.core.db.statuses import RecordStatus
from app.core.service.menu.mapping import DeliveryMapping
from app.interfaces.bot.dialogs.common import CommonEventHandler
from app.interfaces.bot.dialogs.core.decorators import handle_db_errors

from .flow import BuyGoodsFlow
from .states import BuyGoodsSG

import logging

logger = logging.getLogger(__name__)

class BuyGoodsEventHandler(CommonEventHandler):
    """
    Обработчик для buy-goods
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: BuyGoodsFlow
        - States: BuyGoodsSG
    """
    flow: ClassVar[type[BuyGoodsFlow]] = BuyGoodsFlow
    states: ClassVar[type[BuyGoodsSG]] = BuyGoodsSG
    
    @classmethod
    @handle_db_errors
    async def on_price_purchase_typed(
        cls,
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: int,
    ) -> None:
        """
        Обработчик ввода закупочной цены
        
        После ввода создается объект Record
        Price_selling (цена продажи) автоматически устанавливается,
        Если:
            Уже есть эта игра с ценой для продажи
            Игра есть в наличии
        
        Объект форматируется и сразу выводится
        
        Перенаправляется в главное меню
        """
        
        manager.show_mode = ShowMode.EDIT
        
        price_purchase = text
        receive_type = manager.dialog_data.get('receive_type')
        game_name = manager.dialog_data.get('game_name')

        status = (
            RecordStatus.AVAILABLE.value 
            if receive_type == DeliveryMapping.LOCAL 
            else RecordStatus.IN_TRANSIT_TO_ME.value
        )
        
        data = {
            'price_purchase' : price_purchase,
            'status' : status,
        }
        
        record = await cls.flow.create_record_from_game_name(manager, game_name, **data)
        f_record = await cls.flow.set_record_in_dialog_and_format(manager, record.id)
        
        await cls.flow.finish_dialog_with_result(manager, f_record)