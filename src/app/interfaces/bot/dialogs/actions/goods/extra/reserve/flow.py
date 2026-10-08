from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common import CommonFlow

import logging

logger = logging.getLogger(__name__)

class ReserveFlow(CommonFlow):
    
    @classmethod
    async def get_records(cls, manager: DialogManager):
        """
        Переопределение стандартного метода
        Получаем записи определенной игры из наличия
        """
        game_name = manager.dialog_data.get('game_name')
        return await cls.get_available_records_by_game(manager, game_name)
    
        
        