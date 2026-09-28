from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common import CommonGetter

from .flow import OrderArrivedFlow as Flow


class OrderArrivedGetter(CommonGetter):
    
    @classmethod
    async def get_records(cls, dialog_manager: DialogManager):
        """
        Переопределение стандартного метода
        Получаем записи определенной игры и определенного получателя
        """
        return await Flow.get_records(dialog_manager)
        
        