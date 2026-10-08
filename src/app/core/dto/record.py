from typing import NamedTuple

from app.core.db.models import Record

class AvailableRecordDTO(NamedTuple):
    """
    DTO для записей из наличия
    
    Attributes:
        record: объект Record
        game_name: название игры
    """
    
    record: Record
    game_name: str
    