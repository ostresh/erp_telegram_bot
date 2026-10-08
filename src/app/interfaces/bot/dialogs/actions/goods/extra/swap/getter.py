from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common import CommonGetter

from .flow import SwapFlow as Flow


class SwapGetter(CommonGetter):
    
    @classmethod
    async def get_records(cls, dialog_manager: DialogManager):
        """
        Получение записей для выбора в диалоге обмена.

        Логика зависит от типа обмена:
            swap_out → исходящие записи (для отдачи)
            swap_in  → пустой список (входящие выбираются по названию игры,
                        а не из существующих записей)
        """
        
        swap_type = dialog_manager.dialog_data.get('swap_type')
                
        if swap_type == 'swap_out':
            return await Flow.get_records(dialog_manager)
        
        if swap_type == 'swap_in':
            return []
        
        raise ValueError(
            f"Неизвестный или не установленный swap_type: '{swap_type}'. "
            f"Ожидается 'swap_out' или 'swap_in'."
        )
        
        