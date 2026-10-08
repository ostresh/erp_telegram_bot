from typing import ClassVar

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from app.core.db.statuses import RecordStatus
from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors
from app.interfaces.bot.utils.emoji import Emoji

from .states import SwapSG
from .flow import SwapFlow

import logging

logger = logging.getLogger(__name__)

class SwapEventHandler(CommonEventHandler):
    """
    Обработчик для swap
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: SwapFlow
        - States: SwapSG
    """
    flow: ClassVar[type[SwapFlow]] = SwapFlow
    states: ClassVar[type[SwapSG]] = SwapSG
    
    @classmethod
    @handle_db_errors
    async def on_back(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Кнопка "Назад" в непервом окне диалога.

        """
        await callback.answer()

        await manager.switch_to(cls.states.main)
    
    @staticmethod
    @handle_db_errors
    async def on_swap_in_button(
        callback: CallbackQuery, 
        button: Button, 
        manager: DialogManager
    ):
        """
        Обработчик кнопки "ПОЛУЧАЮ"
        """
        
        await callback.answer()
        
        manager.dialog_data['swap_type'] = 'swap_in'
        manager.dialog_data['swap_title'] = f'{Emoji.SWAP_IN} ВХОДЯЩИЕ'
        
        await manager.switch_to(SwapSG.getting_input, show_mode=ShowMode.EDIT)
        
    @staticmethod
    @handle_db_errors
    async def on_swap_out_button(
        callback: CallbackQuery, 
        button: Button, 
        manager: DialogManager
    ):
        """
        Обработчик кнопки "ОТДАЮ"
        """
        
        await callback.answer()
        
        manager.dialog_data['swap_type'] = 'swap_out'
        manager.dialog_data['swap_title'] = f'{Emoji.SWAP_OUT} ИСХОДЯЩИЕ'
        
        await manager.switch_to(SwapSG.giving_input, show_mode=ShowMode.EDIT)
        
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
        
        В зависимости от направления обмена:
            swap_out → выбранная запись добавляется в исходящие
            swap_in  → введённая игра добавляется во входящие
            
        После чего возвращает на главное окно обмена
        """
        
        swap_type = manager.dialog_data.get('swap_type')
        
        if swap_type == 'swap_out':
            if await cls.flow.is_record_id_selected(callback, manager):
                cls.flow.add_game_out(manager)
            else: return
        elif swap_type == 'swap_in':
            cls.flow.add_game_in(manager)
        
        await callback.answer()
            
        await manager.switch_to(state=cls.states.main, show_mode=ShowMode.EDIT)
        
    @classmethod
    @handle_db_errors
    async def on_finish_dialog(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Обработчик завершения диалога
        
        Записывает исходящие игры как SOLD
        Создает записи с входящими играми
        """
        
        used_record_ids: list = manager.dialog_data.get('used_record_ids')
        games_in: list = manager.dialog_data.get('games_in')
        
        if not used_record_ids or not games_in:
            await callback.answer("⚠️ Сначала выберите исходящие и входящие игры!", show_alert=True)
            return
        
        await callback.answer()
        
        new_records = await cls.flow.create_records_from_game_names(
            manager, 
            games_in, 
            **{'status' : RecordStatus.AVAILABLE.value}
        )
        new_record_ids = [record.id for record in new_records]
            
        texts = await cls.flow.apply_swap(manager, used_record_ids, new_record_ids)
        
        manager.show_mode = ShowMode.DELETE_AND_SEND  
        await cls.flow.finish_dialog_with_many_result(manager, texts)
        
        
        