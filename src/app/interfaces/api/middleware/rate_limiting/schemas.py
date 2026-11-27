from pydantic import BaseModel, Field


class RateLimitResult(BaseModel):
    """
    Результат проверки rate limit
    
    Attributes:
        allowed (bool): разрешены ли запросы
        current_count (int): текущее количество запросов в окне
        limit (int): лимит запросов
        remaining (int): сколько запросов осталось
        window_size (int): Размер окна в секундах
    """
    
    allowed: bool = Field(..., description="Разрешены ли запросы")
    current_count: int = Field(..., description="Текущее количество запросов в окне")
    limit: int = Field(..., description="Лимит запросов")
    remaining: int = Field(..., description="Сколько запросов осталось")
    window_size: int = Field(..., description="Размер окна в секундах")