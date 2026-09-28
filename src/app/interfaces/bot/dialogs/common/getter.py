from typing import Any, List, Sequence
from aiogram_dialog import DialogManager

from app.core.db.models import Record
from app.core.service.menu import RecipientMapping, DeliveryMapping


class CommonGetter:
    """
    Базовый Getter
    
    Подклассы переопределяют:
        get_records: получениие записей со своей стратегией поиска
    """
    
    @classmethod
    async def get_records(cls, manager: DialogManager) -> List[Record]:
        """
        Получение записей.

        Переопределяется в каждом диалоговом Getter со своей стратегией поиска.
        """
        
        raise NotImplementedError(
            f"{cls.__name__} must implement get_records"
        )
    
    
    @staticmethod
    async def get_delivery(dialog_manager: DialogManager, **kwargs) -> dict[str, list]:
        """
        Геттер для получения методов продажи товара
        
        Содержит:
            Локально
            С доставкой
        """
        
        return {
            'methods' : DeliveryMapping.METHODS
        }
        
    @staticmethod
    async def get_order_recipient(dialog_manager: DialogManager, **kwargs) -> dict[str, list]:
        """
        Геттер для выбора получателя
        
        Содержит:
            Локально
            С доставкой
        """
        
        return {
            'methods' : RecipientMapping.METHODS,
        }

    @staticmethod
    async def pagination_flags(items: Sequence[Any]) -> dict[str, bool]:
        """
        Флаги размера списка относительно порога пагинации. Для `when` в виджетах.

        Ключи (count = len(items), T = PAGINATION_THRESHOLD):
            needs_scrolling   — count > T: элементов много, нужен ScrollingGroup
            needs_plain_group — 1 < count <= T: элементов немного, хватит обычной Group
            has_multiple      — count > 1: не единственная запись
            is_single         — count == 1: единственная запись (автовыбор)
            is_empty          — count == 0: записей нет (пустое состояние)

        Ключи подмешиваются в данные getter'а, поэтому
        не должны пересекаться с другими ключами данных.

        Args:
            items: коллекция элементов (используется только длина)

        Returns:
            словарь флагов для условного отображения виджетов
        """
        from app.interfaces.bot.dialogs.common import CommonConstants
        count = len(items)
        threshold = CommonConstants.PAGINATION_THRESHOLD.value

        return {
            'needs_scrolling': count > threshold,
            'needs_plain_group': 1 < count <= threshold,
            'has_multiple': count > 1,
            'is_single': count == 1,
            'is_empty': count == 0,
        }
        
    @classmethod
    async def get_records_ids(cls, dialog_manager: DialogManager, **kwargs):
        """
        Получение id записей
        Метод get_records переопределяется
        """
        
        records = await cls.get_records(dialog_manager)
        
        return {
            'game_ids' : [{'id' : record.id} for record in records],
            **(await cls.pagination_flags(records))
        }
        
        