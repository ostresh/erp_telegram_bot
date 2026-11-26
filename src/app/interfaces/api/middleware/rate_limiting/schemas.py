from pydantic import BaseModel, Field


class RateLimitResult(BaseModel):
    """
    Результат проверки rate limit
    
    Attributes:
        allowed (bool): разрешены ли запросы
        current_count (int): текущее количество запросов в окне
        limit (int): лимит запросов
        remaining (int): сколько запросов осталось
        
    """
    
    allowed: bool = Field(..., description="Разрешены ли запросы")
    current_count: int = Field(..., description="Текущее количество запросов в окне")
    limit: int = Field(..., description="Лимит запросов")
    remaining: int = Field(..., description="Сколько запросов осталось")