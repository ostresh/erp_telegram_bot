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

from app.db.unit_of_work import UnitOfWork
from app.service import MenuService


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
          
            
        
        
    