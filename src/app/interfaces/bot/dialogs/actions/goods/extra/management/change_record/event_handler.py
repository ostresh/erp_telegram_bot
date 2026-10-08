from typing import ClassVar

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors
from app.interfaces.bot.utils.message import schedule_message_for_deletion
from app.interfaces.bot.utils.emoji import Emoji

from .states import ChangeRecordSG
from .flow import ChangeRecordFlow

import logging

logger = logging.getLogger(__name__)

class ChangeRecordEventHandler(CommonEventHandler):
    """
    Обработчик для sell-goods
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: ChangeRecordFlow
        - States: ChangeRecordSG
    """
    flow: ClassVar[type[ChangeRecordFlow]] = ChangeRecordFlow
    states: ClassVar[type[ChangeRecordSG]] = ChangeRecordSG
    
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

        Возвращает к предыдущему окну диалога
        Или переопределяется
        """
        await callback.answer()

        await manager.switch_to(cls.states.main)
    
    @classmethod
    @handle_db_errors
    async def on_select_record_id_button(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """Переход к следующему шагу, если выбран record_id"""
        
        if not await cls.flow.is_record_id_selected(callback, manager):
            return
        
        await callback.answer()
        await manager.switch_to(cls.states.main)

    @classmethod
    @handle_db_errors
    async def on_change_attribute_button(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Переводит на окно ввода нового значения для атрибута
        """
        
        manager.dialog_data['attribute'] = button.widget_id
        manager.dialog_data['attribute_title'] = button.text.text
        
        await callback.answer()
        await manager.switch_to(cls.states.change_attribute)
        
        
    @classmethod
    @handle_db_errors
    async def on_change_attribute(
        cls,
        message: Message, 
        widget: TextInput, 
        manager: DialogManager, 
        text: str
    ):
        """
        Изменяет выбранный атрибут
        """
        
        manager.show_mode = ShowMode.EDIT
        
        record_id = manager.dialog_data.get('record_id')
        attribute = manager.dialog_data.get('attribute')
        
        if record_id is None or attribute is None:
            await message.delete()
            await schedule_message_for_deletion(
                await message.answer(
                    f'{Emoji.ERROR} Ошибка: запись или атрибут не выбраны',
                ),
                manager.middleware_data['uow'],
            )
            return
        
        try:
            value = cls.flow.format_value_type(manager, text)
            await message.delete()
        except (ValueError, TypeError):
            await message.delete()
            await schedule_message_for_deletion(
                await message.answer(
                    text = f'{Emoji.ERROR} Введено неправильное значение',
                ),
                manager.middleware_data['uow']
            )
            return
        
        data = {
            attribute : value
        }
            
        await cls._apply_record_update(manager, record_id, **data)
        
    @classmethod
    @handle_db_errors
    async def on_game_attribute_type(
        cls,
        message: Message, 
        widget: TextInput, 
        manager: DialogManager, 
        text: str
    ):
        """
        Изменяет игру
        """
        
        manager.show_mode = ShowMode.EDIT
        
        record_id = manager.dialog_data.get('record_id')
        
        if not await cls.flow.is_game_exists(manager, text.strip()):
            await message.delete()
            return
        
        game_id = (await cls.flow.get_game_from_game_name(manager, text.strip())).id
        
        await message.delete()
        manager.dialog_data.pop('game_error', None)
        
        data = {
            'game_id' : game_id
        }
            
        await cls._apply_record_update(manager, record_id, **data)
        
    @classmethod
    @handle_db_errors
    async def on_change_status(
        cls,
        callback: CallbackQuery, 
        button: Button, 
        manager: DialogManager
    ):
        """
        Изменяет статус
        """
        
        manager.show_mode = ShowMode.EDIT
        
        await callback.answer()
        
        record_id = manager.dialog_data.get('record_id')
        
        status = button.widget_id
        
        data = {
            'status' : status
        }
            
        await cls._apply_record_update(manager, record_id, **data)
        
    @classmethod
    @handle_db_errors
    async def end_dialog(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Завершает диалог
        И выводит пользователю Record
        """
        
        await callback.answer()
        
        f_record = manager.dialog_data.get('f_record', f'{Emoji.ERROR} Произошла ошибка')
        
        await cls.flow.finish_dialog_with_result(manager, f_record)
        
    @classmethod
    @handle_db_errors
    async def _apply_record_update(
        cls,
        manager: DialogManager,
        record_id: int,
        **data
    ) -> None:
        """
        Обновляет record и вставляет в диалог
        Перенаправляет на main
        
        Args:
            manager: DialogManager,
            record_id: id записи
            data: словарь с данными
        """
        
        u_record = await cls.flow.update_record(manager, record_id, **data)
        f_record = await cls.flow.format_record(manager, u_record.id)
        await cls.flow.set_record_in_dialog(manager, record_id, f_record)
        
        await manager.switch_to(cls.states.main)
        
        
        
        
    