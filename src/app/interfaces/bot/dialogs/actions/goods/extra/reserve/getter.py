from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common import CommonGetter

from .flow import ReserveFlow as Flow


class ReserveGetter(CommonGetter):
    
    @classmethod
    async def get_records(cls, dialog_manager: DialogManager):
        """
        Переопределение стандартного метода
        Получаем записи
        """
        return await Flow.get_records(dialog_manager)
        
        