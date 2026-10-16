from typing import ClassVar

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Multiselect

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.common.mapping import PlatformMapping
from app.interfaces.bot.dialogs.core.decorators import handle_db_errors

from .flow import AddGameFlow
from .states import AddGameSG

import logging

logger = logging.getLogger(__name__)

class AddGameEventHandler(CommonEventHandler):
    """
    Обработчик для add_game
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: AddGameFlow
        - States: AddGameSG
    """
    flow: ClassVar[type[AddGameFlow]] = AddGameFlow
    states: ClassVar[type[AddGameSG]] = AddGameSG
    
    @classmethod
    @handle_db_errors
    async def on_game_typed(
        cls,
        message: Message, 
        widget: TextInput, 
        manager: DialogManager,
        text: str
    ):
        """
        Обработчик ввода названия игры
        """
        
        manager.show_mode = ShowMode.EDIT
        
        game_name = text.strip()
        
        manager.dialog_data['game_name'] = game_name
        
        await message.delete()
        
        if await cls.flow.is_game_already_exists(manager, game_name):
            manager.dialog_data['game_error'] = f'Игра {game_name} уже есть в списке!'
            return
        
        manager.dialog_data.pop('game_error', None)
        
        await manager.next(show_mode=ShowMode.EDIT)
        
    @classmethod
    @handle_db_errors
    async def on_platform_select(
        cls,
        callback: CallbackQuery, 
        widget: Multiselect, 
        manager: DialogManager, 
        item_id: str
    ):
        """
        Обработчик нажатия кнопки в multiselect
        """
        
        manager.dialog_data['platforms'] = widget.get_checked()
        
        await manager.update(show_mode=ShowMode.EDIT)
    
    @classmethod
    @handle_db_errors  
    async def end_dialog(
        cls,
        callback: CallbackQuery, 
        button: Button, 
        manager: DialogManager
        ):
        """
        Обработчик нажатия кнопки "Далее"
        
        Сохраняет игру в games_list с выбранными платформами
        """

        platforms = manager.dialog_data.get('platforms')
        game_name = manager.dialog_data.get('game_name')
        
        if not game_name:
            await callback.answer('Не удалось определить название игры', show_alert=True)
            return
        
        if not platforms:
            await callback.answer('Выберите платформу!')
            return
        
        await callback.answer()
        
        prefixes = [
            prefix for prefix in PlatformMapping.PREFIXIES
        ]
        
        game_with_prefixes = [
            f'{prefix} {game_name}'
            for prefix in prefixes
        ]
            
        new_games = await cls.flow.create_games(manager, game_with_prefixes)
        
        manager.show_mode = ShowMode.EDIT
        
        await cls.flow.finish_dialog_with_result(
            manager,
            '\n'.join(new_games)
        )
        