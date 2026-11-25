from enum import Enum
from typing import List

from pydantic import BaseModel, Field, field_validator


class DeliveryType(str, Enum):
    """
    Виды доставок
    
    Properties:
        display_name: возвращает название доставки
    """
    
    POST_RU = "post_ru"
    CDEK = "cdek"
    AVITO = "avito"
    FIVE_POST = "5post"
    DPD = "dpd"
    
    @property
    def display_name(self) -> str:
        """Возвращает название доставки"""
        return {
            "post_ru" : "Почта России",
            "cdek" : "CDEK",
            "avito" : "Aвито",
            "5post" : "5Post",
            "dpd" : "DPD"
        }.get(self.value)
        

class LabelItemDTO(BaseModel):
    """
    Один элемент этикетки
    
    Attributes:
        game_name (str): Название игры
        count (int): Количество
    
    Validators:
        game_name: не может быть пустым, делается strip
    """
    
    game_name: str = Field(..., description="Название игры")
    count: int = Field(..., description="Количество")
    
    @field_validator("game_name", mode="before")
    @classmethod
    def validate_game_name(cls, v: str) -> str:
        """Не может быть пустым, а также делается strip"""
        if not v.strip():
            raise ValueError("game_name не может быть пустым")
        return v.strip()
    
     
class LabelDTO(BaseModel):
    """
    Данные для одной этикетки. Один DTO - одна этикетка
    
    Attributes:
        order_number (str): номер заказа
        delivery (str): доставка
        items (list[LabelItemDTO]): список игр
        
    Validators:
        order_number: убираются все пробелы, остаются только цифры
    """
    
    order_number: str = Field(..., description="Номер заказа")
    delivery: DeliveryType = Field(..., description="Доставка")
    items: List[LabelItemDTO] = Field(..., default_factory=list, min_length=1, description="Список игр")
    
    @field_validator('order_number', mode='before')
    @classmethod
    def validate_order_number(cls, v: str) -> str:
        """Валидация номера заказа, удаляются все пробелы"""
        if not v.strip():
            raise ValueError('Номер заказа не может быть пустым')
        return v.strip().replace(' ', '')
    