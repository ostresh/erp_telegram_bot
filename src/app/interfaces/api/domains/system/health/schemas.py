from typing import Literal, Optional

from pydantic import BaseModel, Field

class ComponentStatus(BaseModel):
    """
    Статус компонента системы
    
    Attributes:
        status (Literal["ok", "error"]): статус компонента, ок или ошибка
        message (Optional[str]): сообщение (опционально)
    """
    
    status: Literal["ok", "error"]
    message: Optional[str] = None
    
    

class HealthResponse(BaseModel):
    """
    Ответ health пробы
    
    Attributes:
        status (Literal["ok", "error"]): статус api, ок или ошибка
    """
    
    status: Literal["ok", "error"]
    
class DetailedHealthResponse(BaseModel):
    """
    Детальный ответ каждого компонента системы
    
    Attributes:
        status (Literal["ok", "degraded", "error"]): общее состяние системы.
        postgres (ComponentStatus): состояние постгреса
        redis (ComponentStatus): состояние редиса
    """
    
    status: Literal["ok", "degraded", "error"]
    
    postgres: ComponentStatus = Field(
        description="состояние PostgreSQL"
    )
    
    redis: ComponentStatus = Field(
        description="состояние Redis"
    )
    
    
    