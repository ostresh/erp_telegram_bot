from typing import List

from aiogram_dialog import DialogManager

from app.core.db.models import Record
from app.interfaces.bot.dialogs.common import CommonFlow

class ChangeSellingPriceFlow(CommonFlow):
    
    @classmethod
    async def get_records(cls, manager: DialogManager) -> List[Record]:
        """
        Получение записей.

        Переопределяется в каждом диалоговом Flow со своей стратегией поиска.
        """
        game_name = manager.dialog_data.get('game_name')
        return await cls.get_available_records_by_game(manager, game_name)
        