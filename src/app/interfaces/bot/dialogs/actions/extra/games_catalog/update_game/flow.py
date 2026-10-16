from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import Game
from app.core.db.unit_of_work import UnitOfWork
from app.core.service.game import GameService
from app.interfaces.bot.dialogs.common import CommonFlow
from app.interfaces.bot.dialogs.common.mapping import PlatformMapping

class UpdateGameFlow(CommonFlow):
    
    @classmethod
    async def get_games(cls, manager: DialogManager, game_names: List[str]) -> List[Game]:
        """
        Получение объектов Game из списка названий игр
        
        Args:
            game_names (list[str]): список названий игр
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = GameService(session)
            games = await service.get_by_names(game_names)
        
        return games
    
    @classmethod
    def build_games_map(
        cls,
        games: list[Game],
        new_game_name: str,
    ) -> dict[int, str]:
        """
        Собирает словарь с новыми названиями игр, сохраняя привязку к id
        и исходному префиксу платформы.


        Args:
            games (list[Game]): Список старых игр с префиксами в названии.
            new_game_name (str): Новое название игры без префикса.

        Returns:
            dict[int, str]: Словарь вида ``{game.id: "префикс новое_название"}``.
        """
        
        prefixes = PlatformMapping.PREFIXIES

        result: dict[int, str] = {}

        for game in games:
            for prefix in prefixes:
                if game.name.startswith(f'{prefix} '):
                    result[game.id] = f'{prefix} {new_game_name}'
                    break
                
        return result
                
    @classmethod
    async def update_games(cls, manager: DialogManager, game_names_map: dict[int, str]) -> List[Game]:
        """
        Обновление Games
        
        Args:
            dict[int, str]: Словарь вида ``{game.id: "префикс новое_название"}``
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = GameService(session)
            new_games = [await service.update(item_id=key, name=value) for key, value in game_names_map.items()]
        
        return new_games

        
        
        
        