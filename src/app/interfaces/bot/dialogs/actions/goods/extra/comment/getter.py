from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common import CommonGetter

from .flow import CommentFlow as Flow


class CommentGetter(CommonGetter):
    
    @classmethod
    async def get_records(cls, dialog_manager: DialogManager):
        """
        Переопределение стандартного метода
        Получаем все записи
        """
        return await Flow.get_records(dialog_manager)
        
        