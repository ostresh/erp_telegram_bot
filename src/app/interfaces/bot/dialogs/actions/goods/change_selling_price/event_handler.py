from typing import ClassVar, List

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput

from app.core.db.models import Record
from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
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
        
        records: List[Record] = await cls.flow.get_records(manager)
        record_ids = [record.id for record in records]
        
        new_records = await cls.flow.update_many_records(manager, record_ids, **data)
            
        if new_records:
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
                {Emoji.ERROR} Записей с данной игрой не найдено
                """
            )
            

    @classmethod
    async def _after_game_input(cls, manager: DialogManager):
        """
        Переопределение стандартного метода (который идет после on_game_typed)
        """

        logger.info(f"Game '{manager.dialog_data.get('game_name')}' found, proceeding to next step")
        await manager.switch_to(
            cls.states.input_price_selling,
            show_mode=ShowMode.EDIT,
        )
        
        
        