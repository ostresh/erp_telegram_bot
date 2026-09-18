from enum import Enum


class RecordStatus(str, Enum):
    """Статусы записей"""
    AVAILABLE = "available"
    SOLD = "sold"
    IN_TRANSIT_TO_ME = "in_transit_to_me"
    IN_TRANSIT_TO_CLIENT = "in_transit_to_client"
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя для пользователя"""
        names = {
            "available": "Да",
            "sold": "Нет",
            "in_transit_to_me": "Едет ко мне",
            "in_transit_to_client": "Едет к покупателю",
        }
        return names[self.value]
    
    @classmethod
    def from_display_name(cls, display_name: str) -> 'RecordStatus':
        """Получить статус по отображаемому имени"""
        for status in cls:
            if status.display_name == display_name:
                return status
        raise ValueError(f"Unknown display name: {display_name}")