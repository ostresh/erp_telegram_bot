from datetime import datetime
from typing import Any

from aiogram.types import CallbackQuery, Message, ContentType
from aiogram.fsm.state import StatesGroup, State

from aiogram_dialog import Dialog, Window, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import (
    Button, SwitchTo, Back, Cancel,
    Group, Row, Column,
    Select, Multiselect, Radio, Checkbox,
    ScrollingGroup, NextPage, PrevPage,
    Url, Counter, Calendar
)


from aiogram_dialog.widgets.text import (
    Const, Format, Jinja, Case, Multi,
)
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.api.exceptions import IncorrectBackgroundError

from app.core.db.unit_of_work import UnitOfWork
from app.core.service import MenuService

import logging

logger = logging.getLogger(__name__)

class CommonEventHandler:
    """
    Общий обработчик событий для диалогов
    """
    
    @staticmethod
    async def on_back(
        callback: CallbackQuery, 
        button: Button, 
        manager: DialogManager
    ):
        """
        Обработчик кнопки "Назад" для первого диалогого окна
        
        Формирует меню, которое было до нажатия кнопки действия
        """
        
        await callback.answer()
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        path = manager.start_data['path']
        
        async with uow() as session:
            service = MenuService(session)
            menu = await service.get_back_menu(path)
        
        await manager.done()
           
        await callback.message.edit_text(
            text = menu.text,
            reply_markup = menu.keyboard
        )
        
    @staticmethod
    async def on_close(
        callback: CallbackQuery, 
        button: Button, 
        manager: DialogManager
    ):
        """
        Обработчик кнопки "Закрыть"
        
        Формирует главное меню
        """
        
        await callback.answer()
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = MenuService(session)
            menu = await service.get_menu('main')
        
        await manager.done()
            
        await callback.message.edit_text(
            text = menu.text,
            reply_markup = menu.keyboard
        )
        
    @staticmethod
    async def on_int_error(
        message: Message, 
        widget: TextInput, 
        manager: DialogManager, 
        error: ValueError):
        """
        Обработчик для ввода цены (int)
        """
        await message.answer("❌ Введите целое число!")
        
    @staticmethod
    async def on_text_error(
        message: Message, 
        widget: TextInput, 
        manager: DialogManager, 
        error: ValueError):
        """
        Обработчик для ввода строки (str)
        """
        await message.answer("❌ Введите правильную строку!")
        
    @staticmethod    
    async def on_receive_method_selected(
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str,
    ) -> None:
        """
        Обработчик выбора метода продажи товара
        (локально или с доставкой)
        """
        
        await callback.answer()
        
        manager.dialog_data['receive_type'] = item_id
        
        receive_title = manager.dialog_data['receive_methods_map'][item_id]
        manager.dialog_data['receive_title'] = receive_title
        
        logger.info(f"Receive method {item_id}, proceeding to next step")
        
        await manager.next(show_mode=ShowMode.EDIT)

          
            
        
        
    