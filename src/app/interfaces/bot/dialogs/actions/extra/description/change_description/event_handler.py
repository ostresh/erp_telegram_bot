from typing import Any, ClassVar
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors

from .states import ChangeDescriptionSG
from .flow import ChangeDescriptionFlow

class ChangeDescriptionEventHandler(CommonEventHandler):
    """
    Обработчик для ChangeDescription
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: ChangeDescriptionFlow
        - States: ChangeDescriptionSG
    """
    flow: ClassVar[type[ChangeDescriptionFlow]] = ChangeDescriptionFlow
    states: ClassVar[type[ChangeDescriptionSG]] = ChangeDescriptionSG
    
    @classmethod
    @handle_db_errors
    async def on_start(cls, start_data: Any, manager: DialogManager):
        """
        Выгружает описание для объявлений
        """
        
        manager.show_mode = ShowMode.DELETE_AND_SEND
        
        desc = await cls.flow.get_description(manager)
        manager.dialog_data['desc'] = desc
        
        event: CallbackQuery = manager.event
        
        message_delete = await event.bot.send_message(
            chat_id=event.message.chat.id,
            text=desc,
            parse_mode=None
        )
        
        manager.dialog_data['message_delete_id'] = message_delete.message_id
        
    @classmethod
    async def on_new_desc_input(
        cls,
        message: Message, 
        widget: TextInput, 
        manager: DialogManager, 
        text: str
    ):
        """
        Обработчик ввода нового описания
        """
        
        manager.show_mode = ShowMode.EDIT
        
        await message.bot.delete_message(
            message_id=manager.dialog_data.get('message_delete_id'),
            chat_id=message.chat.id
        )
        
        desc = text.strip()
        
        new_desc = await cls.flow.update_description(manager, desc)
        
        await cls.flow.finish_dialog_with_result_without_parse_mode(manager, new_desc)