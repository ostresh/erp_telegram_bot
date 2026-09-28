from typing import ClassVar

from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup

from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import (
    Button, Select
)

from aiogram_dialog.widgets.input import TextInput, MessageInput

from app.core.service.menu import DeliveryMapping
from app.interfaces.bot.dialogs.core.decorators import handle_db_errors
from app.interfaces.bot.utils.emoji import Emoji

from .flow import CommonFlow

import logging

logger = logging.getLogger(__name__)

class CommonEventHandler:
    """
    Общий обработчик событий для диалогов
    
    Подклассы переопределяют:
        - Flow: конкретный Flow диалога
        - States: StatesGroup диалога (с конвенционными именами состояний)
    """

    flow: ClassVar[type[CommonFlow]] = CommonFlow
    states: ClassVar[type[StatesGroup]] = None
    
    @classmethod
    @handle_db_errors
    async def on_back(
        cls,
        callback: CallbackQuery, 
        button: Button, 
        manager: DialogManager
    ):
        """
        Обработчик кнопки "Назад" для первого диалогого окна
        
        Формирует меню, которое было до нажатия кнопки действия
        """
        
        await callback.answer()
        
        path = manager.start_data['path']
        
        menu = await cls.flow.get_back_menu(manager, path)
        
        await manager.done()
           
        await callback.message.edit_text(
            text = menu.text,
            reply_markup = menu.keyboard
        )
        
    @classmethod
    @handle_db_errors
    async def on_close(
        cls,
        callback: CallbackQuery, 
        button: Button, 
        manager: DialogManager
    ):
        """
        Обработчик кнопки "Закрыть"
        
        Формирует главное меню
        """
        
        await callback.answer()
        
        main_menu = await cls.flow.get_main_menu(manager)
        
        await manager.done()
            
        await callback.message.edit_text(
            text = main_menu.text,
            reply_markup = main_menu.keyboard
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
    ):
        """
        Обработчик выбора метода продажи товара
        (локально или с доставкой)
        """
        
        await callback.answer()
        
        manager.dialog_data['receive_type'] = item_id
        
        receive_title = DeliveryMapping.TITLES[item_id]
        manager.dialog_data['receive_title'] = receive_title
        
        logger.info(f"Receive method {item_id}, proceeding to next step")
        
        await manager.next(show_mode=ShowMode.EDIT)
        
    @classmethod
    @handle_db_errors
    async def on_record_id_selected(
        cls,
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: int,
    ):
        """
        Обработчик выбора ID записи
        
        Обновляет сообщение и выводит отформатированный Record
        """
        
        await callback.answer()
        
        await cls.flow.set_record_in_dialog_and_format(manager, item_id)


    @classmethod
    @handle_db_errors
    async def on_game_typed(
        cls,
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: str,
    ):
        """
        Обработчик успешного ввода названия игры.
        
        Также здесь проводится проверка, существует ли игра в БД.
        
        Если одна игра доступна, сразу формируется строка для вывода
        Чтобы пользователь не выбирал один id из списка
        
        Перед выводом удаляется сообщение (ввод игры) пользователя.
        """
        
        manager.show_mode = ShowMode.EDIT
        
        game_name = text.strip()
        
        manager.dialog_data['game_name'] = game_name
        manager.dialog_data['emoji_game'] = Emoji.GAME
        
        if not await cls.flow.is_game_exists(manager, game_name):
            await message.delete()
            return
        
        manager.dialog_data.pop('game_error', None)
        await message.delete()
        
        records = await cls.flow.get_records(manager)
        
        if len(records) == 1:
            await cls.flow.set_record_in_dialog_and_format(manager, records[0].id)
            
            logger.info(f"One game '{game_name}' found, switch to select_record_id")
            
            if hasattr(cls.states, 'select_record_id'):
                await manager.switch_to(cls.states.select_record_id, show_mode=ShowMode.EDIT)
            return
            
        logger.info(f"Game '{game_name}' found, proceeding to next step")
        await manager.next(show_mode=ShowMode.EDIT)
        
    @classmethod
    async def on_select_record_id_button(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Обработчик кнопки "Далее"
        Переопределяется в каждом классе
        """
        
        raise NotImplementedError(f"{cls.__name__} must implement on_select_record_id_button")
    
    
    @staticmethod
    async def on_unexpected_message(
        message: Message,
        widget: MessageInput,
        manager: DialogManager,
    ):
        """
        Обработчик ввода неожидаемого сообщения от пользователя
        """
        manager.show_mode = ShowMode.EDIT
        
        await message.delete()
        
