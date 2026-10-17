from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, TypeVar, Generic, Optional, List
from app.core.db.models import Base
from app.core.db.repository.base import BaseRepository
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
RepoType = TypeVar("RepoType", bound=BaseRepository[ModelType])

class BaseService(Generic[ModelType, RepoType]):
    """
    Базовый сервис с общими CRUD операциями.
    """
    
    def __init__(self, session: AsyncSession, repository: RepoType) -> None:
        """
        Инициализация сервиса.

        Args:
            session (AsyncSession): активная сессия БД из UnitOfWork.
            repository (RepoType): экземпляр репозитория для работы с моделью.
        """
        self.session: AsyncSession = session
        self.repo: RepoType = repository
        self.model_name: str = repository.model.__name__
    
    """
    CREATE
    """
    
    async def create(self, item: ModelType) -> ModelType:
        """
        Создать новую запись.

        Args:
            item (ModelType): экземпляр модели для создания.

        Returns:
            ModelType: созданный объект модели.

        Raises:
            Exception: При ошибке создания.
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
            items (List[ModelType]): список экземпляров модели для создания.

        Returns:
            List[ModelType]: список созданных объектов модели.

        Raises:
            Exception: При ошибке создания.
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
            reverse (bool): True для сортировки по убыванию (DESC).

        Returns:
            List[ModelType]: список всех объектов модели.

        Raises:
            Exception: При ошибке получения.
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
            item_id (int): ID записи.

        Returns:
            Optional[ModelType]: объект модели или None, если не найден.

        Raises:
            Exception: При ошибке получения.
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
    
    async def update(self, item_id: int, **data: Any) -> Optional[ModelType]:
        """
        Обновить запись по ID.

        Args:
            item_id (int): ID обновляемой записи.
            **data (Any): поля для обновления.

        Returns:
            Optional[ModelType]: обновлённый объект модели или None, если не найден.

        Raises:
            Exception: При ошибке обновления.
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
            item_id (int): ID удаляемой записи.

        Returns:
            bool: True, если запись удалена, иначе False.

        Raises:
            Exception: При ошибке удаления.
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