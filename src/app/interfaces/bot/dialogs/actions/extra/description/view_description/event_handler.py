from typing import Any, ClassVar

from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors

from .states import ViewDescriptionSG
from .flow import ViewDescriptionFlow

class ViewDescriptionEventHandler(CommonEventHandler):
    """
    Обработчик для ViewDescription
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: ViewDescriptionFlow
        - States: ViewDescriptionSG
    """
    flow: ClassVar[type[ViewDescriptionFlow]] = ViewDescriptionFlow
    states: ClassVar[type[ViewDescriptionSG]] = ViewDescriptionSG
    
    @classmethod
    @handle_db_errors
    async def on_start(cls, start_data: Any, manager: DialogManager):
        """
        Выгружает описание для объявлений
        """
        
        desc = await cls.flow.get_description(manager)
        await cls.flow.finish_dialog_with_result_without_parse_mode(manager, desc)