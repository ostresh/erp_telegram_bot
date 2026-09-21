from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import TypeVar, Generic, Type, Optional, List

from app.core.db.models import Base

import logging

logger = logging.getLogger(__name__)

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
            item - объект модели
            
        Return:
            Объект модели
            
        Raises:
            Exception: При ошибке создания
        """

        logger.debug(f'Creating {self.model.__name__}')

        try:
            self.session.add(item)
            await self.session.flush()
            logger.debug(f'{self.model.__name__} created successfully')
            return item
        except Exception as e:
            logger.exception(f'Error creating {self.model.__name__}: {e}')
            raise
            

    async def create_many(self, items: List[ModelType]) -> List[ModelType]:
        """
        Создать запись

        Args:
            items - список объектов модели

        Return:
            Список объектов модели
            
        Raises:
            Exception: При ошибке создания
        """
        
        logger.debug(f'Creating many {self.model.__name__}')
        
        try:
            self.session.add_all(items)
            await self.session.flush()
            logger.debug(f'{len(items)} {self.model.__name__} records created successfully')
            return items
        except Exception as e:
            logger.exception(f'Error creating many {self.model.__name__}: {e}')
            raise
    
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
            
        Raises:
            Exception: При ошибке чтения
        """

        logger.debug(f"Getting all {self.model.__name__}")

        try:
            stmt = (
                select(self.model)
            )
            if reverse:
                stmt = stmt.order_by(self.model.id.desc())
            else:
                stmt = stmt.order_by(self.model.id.asc())
                
            result = await self.session.execute(stmt)
            items = result.scalars().all()
            
            logger.debug(f"Retrieved {len(items)} {self.model.__name__}")
            return items
        except Exception as e:
            logger.exception(f'Error getting all {self.model.__name__}: {e}')
            raise
    
    async def get_by_id(self, item_id: int) -> Optional[ModelType]:
        """
        Чтение строки по id
        
        Args:
            item_id - id строки 
        
        Return:
            Объект модели или None если не найдено
            
        Raises:
            Exception: При ошибке чтения
        """

        logger.debug(f"Getting {self.model.__name__} by id={item_id}")

        try:
            stmt = (
                select(self.model)
                .where(self.model.id == item_id)
            )
            result = await self.session.execute(stmt)
            item =  result.scalar()
            
            if item:
                logger.debug(f"{self.model.__name__} with id={item_id} found")
            else:
                logger.debug(f"{self.model.__name__} with id={item_id} not found")
            
            return item
        except Exception as e:
            logger.exception(f'Error getting {self.model.__name__} by id {item_id}: {e}')
            raise
    
    """
    UPDATE
    """
    async def update(self, item_id: int, **data) -> Optional[ModelType]:
        """
        Обновление данных в модели
        
        Args:
            item_id - id обновляемой строки
            **data - словарь с полями для обновления
        
        Return:
            Объект модели
            
        Raises:
            Exception: При ошибке обновления
        """
        
        logger.debug(f"Updating {self.model.__name__} with id={item_id}")
        
        try:
            stmt = (
                update(self.model)
                .where(self.model.id == item_id)
                .values(**data)
                .returning(self.model)
            )
            result = await self.session.execute(stmt)
            await self.session.flush()
            item = result.scalar_one_or_none()
            
            if item:
                logger.debug(f"{self.model.__name__} with id={item_id} updated")
            else:
                logger.debug(f"{self.model.__name__} with id={item_id} not found")
            
            return item
        except Exception as e:
            logger.exception(f"Error updating {self.model.__name__}: {e}")
            raise
    
    """
    DELETE
    """
    async def delete(self, item_id: int) -> bool:
        """
        Удаление строки в модели
        
        Args:
            item_id - id удаляемой строки
        
        Return:
            bool удалилась ли строка
            
        Raises:
            Exception: При ошибке удаления
        """
        logger.debug(f"Deleting {self.model.__name__} with id={item_id}")
        
        try:
            stmt = (
                delete(self.model)
                .where(self.model.id == item_id)
            )
            result = await self.session.execute(stmt)
            await self.session.flush()
            
            deleted = result.rowcount > 0
            
            if deleted:
                logger.debug(f"{self.model.__name__} with id={item_id} deleted")
            else:
                logger.debug(f"{self.model.__name__} with id={item_id} not found")
            
            return deleted
        except Exception as e:
            logger.exception(f"Error deleting {self.model.__name__} with id={item_id}: {e}")
            raise
    