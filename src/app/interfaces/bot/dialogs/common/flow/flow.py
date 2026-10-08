from .mixins import (
    GameValidationMixin, 
    RecordOperationsMixin, 
    MenuMixin, 
    DialogCompletionMixin,
    GameOperationsMixin
)

class CommonFlow(
    GameValidationMixin, 
    RecordOperationsMixin, 
    MenuMixin, 
    DialogCompletionMixin,
    GameOperationsMixin
):
    """
    Базовый Flow
    Поведение собирается из миксинов при наследовании
    
    Подклассы переопределяют:
        get_records: получение записей со своей стратегией поиска
    """
    