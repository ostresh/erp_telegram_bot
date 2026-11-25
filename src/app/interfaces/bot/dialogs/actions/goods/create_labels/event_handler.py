from typing import ClassVar

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select, Button
from aiogram_dialog.widgets.input import TextInput

from app.core.dto.labels import DeliveryType, LabelDTO, LabelItemDTO
from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors

from .states import CreateLabelsSG

import logging

logger = logging.getLogger(__name__)

class CreateLabelsEventHandler(CommonEventHandler):
    """
    Обработчик для create_labels
    Наследуется от базового обработчика
    
    Переопределяет:
        - States: CreateLabelsSG
    """
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
        
        await callback.answer(show_alert=True)
        
        manager.dialog_data['delivery_value'] = item_id
        manager.dialog_data['delivery_label'] = DeliveryType(item_id).display_name
        
        await manager.next(show_mode=ShowMode.EDIT)
        
    @staticmethod
    @handle_db_errors
    async def on_order_number_input(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: str,
    ):
        """
        Обработчик ввода номера заказа
        """
        
        manager.dialog_data['order_number'] = text
        
        await message.delete()
        
        await manager.next(show_mode=ShowMode.EDIT)
    
    @classmethod
    async def _after_game_input(cls, manager: DialogManager):
        """
        Хук после выбора игры
        """
        
        game_name = manager.dialog_data.get('game_name')
        
        game_names: list = manager.dialog_data.get('game_names', [])
        
        game_names.append(game_name)
        
        manager.dialog_data['game_names'] = game_names
        
        await manager.switch_to(cls.states.main_game_input, show_mode=ShowMode.EDIT)
    
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
        delivery_value = manager.dialog_data.get('delivery_value')
        game_names: list = manager.dialog_data.get('game_names')
        
        if not game_names:
            await callback.answer('⚠️ Добавьте игры!')
            return
        
        unique_game_names = set(game_names)
        games_count = {item: game_names.count(item) for item in unique_game_names}
        
        new_dto = LabelDTO(
            order_number=order_number,
            delivery=delivery_value,
            items=[
                LabelItemDTO(
                    game_name=key,
                    count=value
                )
                for key, value in games_count.items()
                ]
            )
        
        dto_dump = new_dto.model_dump()
        dto_dump["delivery_label"] = manager.dialog_data.get('delivery_label')
        
        manager.dialog_data.setdefault('dtos', []).append(dto_dump)
        
        # Очистка
        for key in ('order_number', 'delivery_label', 'delivery_value', 'game_names'):
            manager.dialog_data.pop(key, None)
        
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
        
        dtos = [LabelDTO.model_validate(item) for item in dtos]
        
        print(dtos)
        
        # тут будет создание таски селери
        
        
        
        
        
        