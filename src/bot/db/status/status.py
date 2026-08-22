from enum import Enum

class RecordStatus(str, Enum):
    """Статусы для Records"""
    AVAILABLE = "Да"
    SOLD = "Нет"
    IN_TRANSIT_ME = "Едет ко мне"
    IN_TRANSIT_CLIENT = "Едет к покупателю"
    
class BulkOrderStatus(str, Enum):
    """Статусы оптовых заказов"""
    CREATED = "Создан"
    IN_TRANSIT = "В пути"
    COMPLETED = "Завершен"