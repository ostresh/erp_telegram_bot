from datetime import datetime, timezone
from typing import ClassVar
from enum import Enum

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select, Button
from aiogram_dialog.widgets.input import TextInput

from app.core.db.statuses import RecordStatus
from app.core.dto.labels import DeliveryType, LabelDTO, LabelItemDTO
from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors
from app.interfaces.bot.utils.emoji import Emoji

from .states import CreateLabelsSG
from .flow import CreateLabelsFlow

import logging

logger = logging.getLogger(__name__)

class CreateLabelsEventHandler(CommonEventHandler):
    """
    Обработчик для create_labels
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: CreateLabelsFlow
        - States: CreateLabelsSG
    """
    flow: ClassVar[type[CreateLabelsFlow]] = CreateLabelsFlow
    states: ClassVar[type[CreateLabelsSG]] = CreateLabelsSG
    
    @classmethod
    @handle_db_errors
    async def on_delivery_selected(
        cls,
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str,
    ):
        """
        Обработчик выбора доставки
        """
        
        await callback.answer()
        
        manager.dialog_data['delivery'] = DeliveryType(item_id)
        
        await manager.next(show_mode=ShowMode.EDIT)
        
    @staticmethod
    @handle_db_errors
    async def on_order_number_input(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: int,
    ):
        """
        Обработчик ввода номера заказа
        """
        
        manager.show_mode = ShowMode.EDIT
        
        manager.dialog_data['order_number'] = text
        
        await message.delete()
        
        await manager.next(show_mode=ShowMode.EDIT)
    
    @classmethod
    @handle_db_errors
    async def on_add_comment_button(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Обработчик нажатия на кнопку для ввода комментария
        """
        
        await callback.answer()
        
        await manager.switch_to(cls.states.input_comment)
    
    @classmethod
    async def _after_game_input(cls, manager: DialogManager):
        """
        Хук после выбора игры
        """
        
        game_name = manager.dialog_data.get('game_name')
        print(game_name)
        
        game_names: list = manager.dialog_data.get('game_names', [])
        
        game_names.append(game_name)
        
        manager.dialog_data['game_names'] = game_names
        
        await manager.switch_to(cls.states.main_game_input)
    
    @classmethod
    @handle_db_errors
    async def create_order(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Обработчик создания LabelDTO
        """
        
        order_number = manager.dialog_data.get('order_number')
        delivery = manager.dialog_data.get('delivery')
        game_names: list = manager.dialog_data.get('game_names')
        
        if not game_names:
            await callback.answer('⚠️ Добавьте игры!')
            return
        
        unique_game_names = set(game_names)
        games_count = {item: game_names.count(item) for item in unique_game_names}
        
        dtos = manager.dialog_data.get('dtos', [])
        
        dtos.append(
            LabelDTO(
            order_number=order_number,
            delivery=delivery.value,
            items=[
                LabelItemDTO(
                    game_name=key,
                    count=value
                )
                for key, value in games_count.items()
                ]
            )
        )
        
        manager.dialog_data['dtos'] = dtos
        
        manager.dialog_data.pop('order_number')
        manager.dialog_data.pop('delivery')
        manager.dialog_data.pop('game_names')
        
        await manager.switch_to(cls.states.main, show_mode=ShowMode.EDIT)
    
    @classmethod
    @handle_db_errors
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
        
        dtos = manager.dialog_data.get('dtos')
        
        if not dtos:
            await callback.answer('⚠️ Добавьте заказы!')
            
        # тут будет создание таски селери
        
        
        
        
        
        