from typing import ClassVar

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select, Button
from aiogram_dialog.widgets.input import TextInput

from app.core.db.statuses.record import RecordStatus
from app.interfaces.bot.dialogs.common import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors
from app.interfaces.bot.utils.emoji import Emoji

from .states import AddTrnsSG
from .flow import AddTrnsFlow

import logging

logger = logging.getLogger(__name__)

class AddTrnsEventHandler(CommonEventHandler):
    """
    Обработчик для order-arrived
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: AddTrnsFlow
        - States: AddTrnsSG
    """
    flow: ClassVar[type[AddTrnsFlow]] = AddTrnsFlow
    states: ClassVar[type[AddTrnsSG]] = AddTrnsSG
    
    @classmethod
    @handle_db_errors
    async def on_trns_selected(
        cls,
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str,
    ):
        """
        Обработчик выбора транзакции
        """
        
        util = await cls.flow.get_util_by_id(manager, int(item_id))
        
        manager.dialog_data['util_id'] = util.id
        manager.dialog_data['util_title'] = util.title
        
        await manager.next()
        
    @staticmethod
    async def on_price_purchase_input(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: int,
    ):
        """
        Обработчик ввода расхода
        """
        
        manager.show_mode = ShowMode.EDIT
        
        manager.dialog_data['price_purchase'] = text
        
        await message.delete()
        
        await manager.next(show_mode=ShowMode.EDIT)
    
    @classmethod
    async def on_add_comment_button(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Обработчик нажатия на кнопку для ввода комментария
        """
        
        await manager.switch_to(cls.states.input_comment)
        
    @classmethod
    async def on_comment_input(
        cls,
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: str,
    ):
        """
        Обработчик ввода комментария
        """
        
        manager.dialog_data['comment'] = text
        manager.dialog_data['emoji'] = Emoji.COMMENT
        
        await message.delete()
        
        await manager.switch_to(cls.states.end_dialog, show_mode=ShowMode.EDIT)
    
    @classmethod
    async def on_end_dialog(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Обработчик завершения диалога
        
        Создает trns и присылает пользователю
        """
        
        data = {
            'util_id' : manager.dialog_data.get('util_id'),
            'price_purchase' : manager.dialog_data.get('price_purchase'),
            'comment' : manager.dialog_data.get('comment'),
            'status' : RecordStatus.SOLD.value
        }
        
        n_record = await cls.flow.create_record(manager, **data)
        f_record = await cls.flow.set_record_in_dialog_and_format(manager, n_record.id)
        
        await cls.flow.finish_dialog_with_result(manager, f_record)
        
        
        
        
        