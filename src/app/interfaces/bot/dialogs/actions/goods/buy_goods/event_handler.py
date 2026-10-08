from typing import ClassVar

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput

from app.core.db.statuses import RecordStatus
from app.interfaces.bot.dialogs.common.mapping import DeliveryMapping
from app.interfaces.bot.dialogs.common import CommonEventHandler, CommonFlow
from app.interfaces.bot.dialogs.core.decorators import handle_db_errors

from .states import BuyGoodsSG

import logging

logger = logging.getLogger(__name__)

class BuyGoodsEventHandler(CommonEventHandler):
    """
    Обработчик для buy-goods
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: CommonFlow
        - States: BuyGoodsSG
    """
    flow: ClassVar[type[CommonFlow]] = CommonFlow
    states: ClassVar[type[BuyGoodsSG]] = BuyGoodsSG
    
    
    @classmethod
    async def _after_game_input(cls, manager: DialogManager):
        """
        Переопределение стандартного метода (который идет после on_game_typed)
        """

        logger.info(f"Game '{manager.dialog_data.get('game_name')}' found, proceeding to next step")
        await manager.switch_to(
            cls.states.receive_method,
            show_mode=ShowMode.EDIT,
        )
    
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
        f_record = await cls.flow.format_record(manager, record.id)
        
        await cls.flow.finish_dialog_with_result(manager, f_record)