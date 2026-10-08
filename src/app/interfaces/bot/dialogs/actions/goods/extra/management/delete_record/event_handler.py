from typing import ClassVar

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors
from app.interfaces.bot.utils.emoji import Emoji

from .states import DeleteRecordSG
from .flow import DeleteRecordFlow

import logging

logger = logging.getLogger(__name__)

class DeleteRecordEventHandler(CommonEventHandler):
    """
    Обработчик для sdelete-record
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: DeleteRecordFlow
        - States: DeleteRecordSG
    """
    flow: ClassVar[type[DeleteRecordFlow]] = DeleteRecordFlow
    states: ClassVar[type[DeleteRecordSG]] = DeleteRecordSG
    
    
    @classmethod
    @handle_db_errors
    async def on_record_id_typed(
        cls,
        message: Message, 
        widget: TextInput, 
        manager: DialogManager, 
        text: int
    ):
        """Вывод введенного id"""
        
        manager.show_mode = ShowMode.EDIT
        
        record_id = text
        
        record = await cls.flow.get_record_by_id(manager, record_id)
        
        if record:
            f_record = await cls.flow.format_record(manager, record.id)
            await cls.flow.set_record_in_dialog(manager, record_id, f_record)
            manager.dialog_data.pop('record_error', None)
        else:
            manager.dialog_data['record_error'] = f'{Emoji.ERROR} Запись не найдена'
        
        await message.delete()
        
        await manager.update(show_mode=ShowMode.EDIT)
    
    @classmethod
    @handle_db_errors
    async def end_dialog(
        cls,
        callback: CallbackQuery, 
        button: Button, 
        manager: DialogManager
    ):
        """Завершение диалога"""
        
        record_id = manager.dialog_data.get('record_id')
        
        if not await cls.flow.is_record_id_selected(callback, manager):
            return
        
        is_deleted = await cls.flow.delete_record(manager, record_id)
        
        if is_deleted:
            await cls.flow.finish_dialog_with_result(
                manager,
                f'{Emoji.STATUS} Запись {Emoji.ID} {record_id} успешно удалена!'
            )
        else:
            await cls.flow.finish_dialog_with_result(
                manager,
                f'{Emoji.ERROR} Произошла ошибка'
            )