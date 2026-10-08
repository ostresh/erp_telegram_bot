from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common import CommonGetter

from .flow import SellGoodsFlow as Flow

class SellGoodsGetter(CommonGetter):
    
    @classmethod
    async def get_records(cls, manager: DialogManager):
        """
        Переопределение стандартного метода
        Получаем записи
        """
        return await Flow.get_records(manager)