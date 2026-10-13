from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common.getter import CommonGetter

from .flow import AddDeliveryToBulkOrderFlow as Flow


class AddDeliveryToBulkOrderGetter(CommonGetter):
    
    @classmethod
    async def get_bulk_order_ids(cls, dialog_manager: DialogManager, **kwargs):
        """
        Получение id оптовых заказов, которые едут ко мне
        """
        
        bulk_orders = await Flow.get_created_bulk_orders(dialog_manager)
        
        return {
            'bulk_order_ids' : [{'id' : bulk_order.id} for bulk_order in bulk_orders],
            **(await cls.pagination_flags(bulk_orders))
        }
        