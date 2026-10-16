from typing import ClassVar

from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core.decorators import handle_db_errors
from app.interfaces.bot.utils.emoji import Emoji

from .flow import DeleteGameFlow
from .states import DeleteGameSG

import logging

logger = logging.getLogger(__name__)

class DeleteGameEventHandler(CommonEventHandler):
    """
    Обработчик для delete_game
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: DeleteGameFlow
        - States: DeleteGameSG
    """
    flow: ClassVar[type[DeleteGameFlow]] = DeleteGameFlow
    states: ClassVar[type[DeleteGameSG]] = DeleteGameSG
    
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
        
        game_name = text.strip()
        
        if not await cls.flow.is_game_exists(manager, game_name):
            await message.delete()
            return
        
        variants = cls.flow.get_names_with_prefixes(game_name)
        games = await cls.flow.get_games(manager, variants)
        
        is_deleted = await cls.flow.delete_games(manager, [game.id for game in games])
        
        if is_deleted:
            await cls.flow.finish_dialog_with_result(
                manager,
                text=f'{Emoji.STATUS} Успешное удаление {game_name} из списка и всех сопутствующих'
            )
        else:
            await cls.flow.finish_dialog_with_result(
                manager,
                text=f'{Emoji.ERROR} Произошла ошибка'
            )
            
    
        