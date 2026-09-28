from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common import CommonGetter

from .flow import ChangeSellingPriceFlow as Flow


class ChangeSellingPriceGetter(CommonGetter):
    
    @classmethod
    async def get_records(cls, dialog_manager: DialogManager):
        """
        Переопределение стандартного метода
        Получаем записи определенной игры и определенного получателя
        """
        return await Flow.get_records(dialog_manager)
    
    @classmethod
    async def get_prices_selling(
        cls,
        dialog_manager: DialogManager,
        **kwargs
    ):
        """
        Получаем цены для продажи для определенной игры
        """
        
        prices = {item.price_selling for item in (await cls.get_records(dialog_manager))}
        
        prices.discard(None)
        
        prices = sorted(list(prices), reverse=True)
        
        return {
            'prices' : ", ".join(map(str, prices))
        }
        