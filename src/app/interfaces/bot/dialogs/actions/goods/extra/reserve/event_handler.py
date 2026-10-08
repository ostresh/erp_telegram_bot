from typing import ClassVar

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors

from .states import ReserveSG
from .flow import ReserveFlow

import logging

logger = logging.getLogger(__name__)

class ReserveEventHandler(CommonEventHandler):
    """
    Обработчик для reserve
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: ReserveFlow
        - States: ReserveSG
    """
    flow: ClassVar[type[ReserveFlow]] = ReserveFlow
    states: ClassVar[type[ReserveSG]] = ReserveSG
    
    
    
    @classmethod
    @handle_db_errors
    async def on_reserve_typed(
        cls,
        message: Message, 
        widget: TextInput, 
        manager: DialogManager, 
        text: str
    ):
        """
        Обработчик ввода информации о брони
        
        Обновляет запись, записывает информацию о брони
        """
        
        manager.show_mode = ShowMode.EDIT
        
        reserve_text = text.strip()
        record_id = manager.dialog_data.get('record_id')
        
        u_record = await cls.flow.update_record(manager, record_id, reserve=reserve_text)
        f_record = await cls.flow.format_record(manager, u_record.id)
        
        await cls.flow.finish_dialog_with_result(manager, f_record)
        
    @classmethod
    @handle_db_errors
    async def on_select_record_id_button(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Переопределение кнопки "Далее"
        """
        
        if not await cls.flow.is_record_id_selected(callback, manager):
            return
        
        await callback.answer()
        await manager.switch_to(state=cls.states.reserve_input, show_mode=ShowMode.EDIT)
        
        
        
        