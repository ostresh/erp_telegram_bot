from pydantic import BaseModel, Field, field_validator

class BulkOrderItemDTO(BaseModel):
    """
    Одна позиция для игры в оптовом заказе
    
    Attributes:
        game_name (str): Название игры
        count (int): Количество
        price_purchase (int): Цена за штуку
       
    Properties:
        total_cost (int): цена одного item
        
    Validators:
        game_name: Строка не может быть пустой, также делается strip
    """
    
    game_name: str = Field(..., description='Название игры')
    count: int = Field(..., gt=0, description='Количество')
    price_purchase: int = Field(..., gt=0, description='Цена за штуку')
    
    @field_validator('game_name')
    @classmethod
    def validate_game_name(cls, v: str) -> str:
        """Валидация game_name: не может быть пустым"""
        if not v.strip():
            raise ValueError('game_name не может быть пустым')
        return v.strip()
    
    @property
    def total_cost(self) -> int:
        """Полная стоимость item"""
        return self.count * self.price_purchase
    
class BulkOrderJsonDTO(BaseModel):
    """
    Входной формат для создания оптового заказа
    
    Attributes:
        seller (str): Продавец
        items (BulkOrderItemDTO): Список позиций
        
    Properties:
        unique_game_names (list[str]): уникальные названия игр из всего заказа
        total_count (int): общее количество позиций в заказе
        total_cost (int): общая стоимость заказа
    
    Validators:
        seller: Не может быть пустым, также делается strip
    """
    
    seller: str = Field(..., description='Продавец')
    items: list[BulkOrderItemDTO] = Field(..., min_length=1, description='Список позиций')
    
    @field_validator('seller')
    @classmethod
    def validate_seller(cls, v: str) -> str:
        """Валидация seller: не может быть пустым"""
        if not v.strip():
            raise ValueError('seller не может быть пустым')
        return v.strip()
    
    @property
    def unique_game_names(self) -> list[str]:
        """Уникализация названия игр во всем заказе"""
        return list({item.game_name for item in self.items})
    
    @property
    def total_count(self) -> int:
        """Общее количество позиций в заказе"""
        return sum(item.count for item in self.items)
    
    @property
    def total_cost(self) -> int:
        """Общая сумма заказа"""
        return sum(item.total_cost for item in self.items)
    
    
        
    

