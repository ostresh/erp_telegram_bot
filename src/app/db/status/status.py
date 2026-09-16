from enum import Enum

class RecordStatus(str, Enum):
    """Статусы для Records"""
    AVAILABLE = "Да"
    SOLD = "Нет"
    DELIVERY_TO_ME = "Едет ко мне"
    DELIVERY_TO_CLIENT= "Едет к покупателю"
    
class BulkOrderStatus(str, Enum):
    """Статусы оптовых заказов"""
    CREATED = "Создан"
    IN_TRANSIT = "В пути"
    COMPLETED = "Завершен"