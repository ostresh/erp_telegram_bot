from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Generic, Optional, List
from app.db.models import Base
from app.db.repository.base import BaseRepository
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
RepoType = TypeVar("RepoType", bound=BaseRepository)

class BaseService(Generic[ModelType, RepoType]):
    """
    Базовый сервис с общими CRUD операциями.
    """
    
    def __init__(self, session: AsyncSession, repository: RepoType):
        """
        Инициализация сервиса.
        
        Args:
            session: Активная сессия БД из UnitOfWork
            repository: Экземпляр репозитория для работы с моделью
        """
        self.session = session
        self.repo = repository
        self.model_name = repository.model.__name__
    
    """
    CREATE
    """
    
    async def create(self, item: ModelType) -> ModelType:
        """
        Создать новую запись.
        
        Args:
            item: Экземпляр модели для создания
            
        Returns:
            Созданный объект модели
            
        Raises:
            Exception: При ошибке создания
        """
        
        logger.info(f'Creating {self.model_name}')
        
        try:
            created_item = await self.repo.create(item)
            logger.info(f"{self.model_name} created successfully")
            return created_item
        except Exception as e:
            logger.exception(f"Error creating {self.model_name}: {e}")
            raise
    
    async def create_many(self, items: List[ModelType]) -> List[ModelType]:
        """
        Создать несколько записей.
        
        Args:
            items: Список экземпляров модели для создания
            
        Returns:
            Список созданных объектов модели
            
        Raises:
            Exception: При ошибке создания
        """
        
        logger.info(f'Creating many {self.model_name}')
        
        try:
            created_items = await self.repo.create_many(items)
            logger.info(f"{len(items)} {self.model_name} records created")
            return created_items
        except Exception as e:
            logger.exception(f"Error creating multiple {self.model_name}: {e}")
            raise
    
    """
    READ
    """
    
    async def get_all(self, reverse: bool = False) -> List[ModelType]:
        """
        Получить все записи.
        
        Args:
            reverse: True для сортировки по убыванию (DESC)
            
        Returns:
            Список всех объектов модели
            
        Raises:
            Exception: При ошибке получения
        """
        
        logger.info(f"Getting all {self.model_name}")
        
        try:
            items = await self.repo.get_all(reverse=reverse)
            logger.info(f"Retrieved {len(items)} {self.model_name} records")
            return items
        except Exception as e:
            logger.exception(f"Error getting all {self.model_name}: {e}")
            raise
    
    async def get_by_id(self, item_id: int) -> Optional[ModelType]:
        """
        Получить запись по ID.
        
        Args:
            item_id: ID записи
            
        Returns:
            Объект модели или None, если не найден
            
        Raises:
            Exception: При ошибке получения
        """
        
        logger.info(f"Getting {self.model_name} by id={item_id}")
        
        try:
            item = await self.repo.get_by_id(item_id)
            if item:
                logger.info(f"{self.model_name} with id={item_id} found")
            else:
                logger.warning(f"{self.model_name} with id={item_id} not found")
            return item
        except Exception as e:
            logger.exception(f"Error getting {self.model_name} by id={item_id}: {e}")
            raise
    
    """
    UPDATE
    """
    
    async def update(self, item_id: int, **data) -> Optional[ModelType]:
        """
        Обновить запись по ID.
        
        Args:
            item_id: ID обновляемой записи
            **data: Поля для обновления
            
        Returns:
            Обновленный объект модели или None, если не найден
            
        Raises:
            Exception: При ошибке обновления
        """
        
        logger.info(f"Updating {self.model_name} with id={item_id}")
        
        try:
            updated_item = await self.repo.update(item_id, **data)
            if updated_item:
                logger.info(f"{self.model_name} with id={item_id} updated")
            else:
                logger.warning(f"{self.model_name} with id={item_id} not found for update")
            return updated_item
        except Exception as e:
            logger.exception(f"Error updating {self.model_name} with id={item_id}: {e}")
            raise
    
    """
    DELETE
    """
    
    async def delete(self, item_id: int) -> bool:
        """
        Удалить запись по ID.
        
        Args:
            item_id: ID удаляемой записи
            
        Returns:
            True если запись удалена, иначе False
            
        Raises:
            Exception: При ошибке удаления
        """
        
        logger.info(f"Deleting {self.model_name} with id={item_id}")
        
        try:
            deleted = await self.repo.delete(item_id)
            if deleted:
                logger.info(f"{self.model_name} with id={item_id} deleted")
            else:
                logger.warning(f"{self.model_name} with id={item_id} not found for deletion")
            return deleted
        except Exception as e:
            logger.exception(f"Error deleting {self.model_name} with id={item_id}: {e}")
            raise