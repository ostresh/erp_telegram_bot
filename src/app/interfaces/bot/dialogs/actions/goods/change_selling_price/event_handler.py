from typing import ClassVar, List

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput

from app.core.db.models import Record
from app.core.db.statuses import RecordStatus
from app.core.service.menu.mapping import DeliveryMapping
from app.interfaces.bot.dialogs.common import CommonEventHandler
from app.interfaces.bot.dialogs.core.decorators import handle_db_errors
from app.interfaces.bot.utils.emoji import Emoji

from .flow import ChangeSellingPriceFlow
from .states import ChangeSellingPriceSG

import logging

logger = logging.getLogger(__name__)

class ChangeSellingPriceEventHandler(CommonEventHandler):
    """
    Обработчик для change_selling_price
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: ChangeSellingPriceFlow
        - States: ChangeSellingPriceSG
    """
    flow: ClassVar[type[ChangeSellingPriceFlow]] = ChangeSellingPriceFlow
    states: ClassVar[type[ChangeSellingPriceSG]] = ChangeSellingPriceSG
    
    @classmethod
    @handle_db_errors
    async def on_input_price_selling(
        cls,
        message: Message, 
        widget: TextInput, 
        manager: DialogManager,
        text: int
    ):
        """
        Обработчик ввода цены для продажи
        
        Изменяет price_selling во всех записях определенной игры
        """
        
        data = {
            'price_selling' : text
        }
        
        records: List[Record] = manager.dialog_data.get('records')
        
        new_records = []
        
        for record in records:
            new_record = await cls.flow.update_record(manager, record.id, **data)
            new_records.append(new_record)
            
        is_success = any(isinstance(record, Record) for record in new_records)
        
        if is_success:
            await cls.flow.finish_dialog_with_result(
                manager,
                (
                    f"<b>{Emoji.STATUS} Успешное изменение цены:\n\n"
                    f"{Emoji.GAME} ИГРА: {manager.dialog_data.get('game_name')}\n\n"
                    f"{Emoji.PRICE_SELLING} ЦЕНА ДЛЯ ПРОДАЖИ: {text}</b>" 
                )
            )
        else:
            await cls.flow.finish_dialog_with_result(
                manager,
                f"""
                {Emoji.ERROR} Произошла ошибка
                """
            )
            
        
        
        