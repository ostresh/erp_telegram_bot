from dataclasses import dataclass
from typing import List, Optional
from fastapi import APIRouter

@dataclass(frozen=True)
class RouterConfig:
    """
    Конфигурация для регистрации роутеров
    
    Attributes:
        router (APIRouter): роутер
        prefix (str): префикс для роутера
        tags (Optional[List[str]]): теги для роутера
    """
    
    router: APIRouter
    prefix: str
    tags: Optional[List[str]] = None
    