from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Generic, Type, Optional, List, Any

from bot.db.models import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий для CRUD операций"""
    
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model
    
    """
    CREATE
    """
    async def create(self, item: ModelType) -> ModelType:
        """
        Создать запись
        
        Args:
            **data - словарь с required полями для создания
            
        Return:
            Объект модели
        """
    
        await self.session.add(item)
        await self.session.flush()
        return item
    
    async def create_many(self, items: List[ModelType]) -> List[ModelType]:
        """
        Создать запись

        Args:
            **data - словарь с required полями для создания

        Return:
            Список объектов модели
        """
        
        await self.session.add_all(items)
        await self.session.flush()
        return items
    
    """
    READ
    """
    async def get_all(self, reverse: bool = False) -> List[ModelType]:
        """
        Чтение всех строк модели
        
        Args:
            reverse - сортировка в обратном порядке (DESC)
        
        Return:
            Список объектов модели
        """

        stmt = (
            select(self.model)
        )
        if reverse:
            stmt = stmt.order_by(self.model.id.desc())
        else:
            stmt = stmt.order_by(self.model.id.asc())
            
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_id(self, item_id: int) -> List[ModelType]:
        """
        Чтение строки по id
        
        Args:
            item_id - id строки 
        
        Return:
            Объект модели
        """

        stmt = (
            select(self.model)
            .where(self.model.id == item_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar()
    
    """
    UPDATE
    """
    async def update(self, item_id: int, **data) -> Optional[ModelType]:
        """
        Обновление данных в модели
        
        Args:
            record_id - id обновляемой строки
            **data - словарь с полями для обновления
        
        Return:
            Объект модели
        """
        stmt = (
            update(self.model)
            .where(self.model.id == item_id)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()
    
    """
    DELETE
    """
    async def delete(self, item_id: int) -> bool:
        """
        Удаление строки в модели
        
        Args:
            record_id - id удаляемой строки
        
        Return:
            bool удалилась ли строка
        """
        stmt = (
            delete(self.model)
            .where(self.model.id == item_id)
            )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
    