from enum import Enum


class BulkOrderStatus(str, Enum):
    """Статусы оптовых заказов"""
    
    CREATED = "created"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя для пользователя"""
        names = {
            "created": "Создан",
            "in_transit": "В пути",
            "completed": "Завершён",
        }
        return names[self.value]
    
    @classmethod
    def from_display_name(cls, display_name: str) -> 'BulkOrderStatus':
        """Получить статус по отображаемому имени"""
        for status in cls:
            if status.display_name == display_name:
                return status
        raise ValueError(f"Unknown display name: {display_name}")