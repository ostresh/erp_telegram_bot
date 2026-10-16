from typing import ClassVar

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core.decorators import handle_db_errors
from app.interfaces.bot.utils.emoji import Emoji

from .flow import UpdateGameFlow
from .states import UpdateGameSG

import logging

logger = logging.getLogger(__name__)

class UpdateGameEventHandler(CommonEventHandler):
    """
    Обработчик для update_game
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: UpdateGameFlow
        - States: UpdateGameSG
    """
    flow: ClassVar[type[UpdateGameFlow]] = UpdateGameFlow
    states: ClassVar[type[UpdateGameSG]] = UpdateGameSG
    
    @classmethod
    @handle_db_errors
    async def on_new_name_typed(
        cls,
        message: Message, 
        widget: TextInput, 
        manager: DialogManager,
        text: str
    ):
        """
        Обработчик ввода названия игры
        """
        
        game_name = manager.dialog_data.get('game_name')
        new_game_name = text.strip()
        
        variants = cls.flow.get_names_with_prefixes(game_name)
        games = await cls.flow.get_games(manager, variants)
        new_games_map = cls.flow.build_games_map(games, new_game_name)
        
        new_games = await cls.flow.update_games(manager, new_games_map)
        
        if None not in new_games:
            await cls.flow.finish_dialog_with_result(
                manager,
                '\n'.join(game.name for game in new_games)
            )
        else:
            await cls.flow.finish_dialog_with_result(
                manager,
                text=f'{Emoji.ERROR} Произошла ошибка'
            )
        
    @classmethod
    async def _after_game_input(cls, manager: DialogManager):
        """
        После выбора игры
        """

        await manager.next(show_mode=ShowMode.EDIT)
    
        