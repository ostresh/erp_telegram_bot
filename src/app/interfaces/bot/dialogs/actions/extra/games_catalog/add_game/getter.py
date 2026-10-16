from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common import CommonGetter


class AddGameGetter(CommonGetter):
    
    @classmethod
    async def get_platforms(cls, dialog_manager: DialogManager, **kwargs):
        """
        Переопределение стандартного метода
        Получаем записи определенной игры и определенного получателя
        """
        return {'platforms': [
            {'id' : 'PS5'},
            {'id' : 'PS4'}
        ]}
    
        