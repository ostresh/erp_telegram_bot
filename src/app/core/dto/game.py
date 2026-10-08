from typing import NamedTuple, Optional
from app.core.db.models import Game

class AvailableGameDTO(NamedTuple):
    """
    DTO для игр в наличии
    
    Attributes:
        game: объект Game(id, name)
        price_purchase: цена покупки
        price_selling: цена для продажи
        games_count: количество игр (группировка по названию)
    """
    game: Game
    price_purchase: Optional[int]
    price_selling: Optional[int]
    games_count: Optional[int]
    