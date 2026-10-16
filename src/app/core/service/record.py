from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.db.repository import RecordRepository
from app.core.db.models import Record
from app.core.db.statuses import RecordStatus
from app.core.dto import AvailableRecordDTO
from app.core.service.base import BaseService

import logging

logger = logging.getLogger(__name__)


class RecordService(BaseService[Record, RecordRepository]):
    """Сервис для работы с Record"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, RecordRepository(session))

    # Checks

    async def is_game_available(self, game_name: str) -> bool:
        """Проверяет, есть ли игра в наличии.

        Args:
            game_name (str): название игры.

        Returns:
            bool: True, если игра доступна, иначе False.
        """
        try:
            return await self.repo.is_game_available(game_name)
        except Exception:
            logger.exception("Error checking game available")
            raise

    # Read operations

    async def get_available(self) -> List[AvailableRecordDTO]:
        """Получает все доступные записи с названиями игр.

        Returns:
            List[AvailableRecordDTO]: список доступных записей с названием игры.
        """
        try:
            return await self.repo.get_available()
        except Exception:
            logger.exception("Error getting available records")
            raise

    async def get_in_transit_to_me(self) -> List[Record]:
        """Получает все записи, которые едут ко мне.

        Returns:
            List[Record]: список записей в пути ко мне.
        """
        try:
            return await self.repo.get_in_transit_to_me()
        except Exception:
            logger.exception("Error getting in transit to me records")
            raise

    async def get_in_transit_to_client(self) -> List[Record]:
        """Получает все записи, которые едут к покупателю.

        Returns:
            List[Record]: список записей в пути к покупателю.
        """
        try:
            return await self.repo.get_in_transit_to_client()
        except Exception:
            logger.exception("Error getting in transit to client records")
            raise

    # Game-specific reads

    async def get_by_game(
        self,
        game_name: str,
        status: Optional[RecordStatus] = None,
    ) -> List[Record]:
        """Получает записи по названию игры и опциональному статусу.

        Args:
            game_name (str): название игры.
            status (Optional[RecordStatus]): статус записи. Если не указан, возвращает все записи игры.

        Returns:
            List[Record]: список записей по заданным условиям.
        """
        try:
            return await self.repo.get_by_game(game_name, status)
        except Exception:
            logger.exception("Error getting records by game")
            raise

    async def get_available_by_game(self, game_name: str) -> List[Record]:
        """Получает доступные записи по названию игры.

        Args:
            game_name (str): название игры.

        Returns:
            List[Record]: список доступных записей игры.
        """
        try:
            return await self.repo.get_by_game(game_name, RecordStatus.AVAILABLE)
        except Exception:
            logger.exception("Error getting available records by game")
            raise

    async def get_in_transit_to_client_by_game(self, game_name: str) -> List[Record]:
        """Получает записи, которые едут к клиенту, по названию игры.

        Args:
            game_name (str): название игры.

        Returns:
            List[Record]: список записей игры в пути к клиенту.
        """
        try:
            return await self.repo.get_by_game(game_name, RecordStatus.IN_TRANSIT_TO_CLIENT)
        except Exception:
            logger.exception("Error getting in transit to client records by game")
            raise

    async def get_in_transit_to_me_by_game(self, game_name: str) -> List[Record]:
        """Получает записи, которые едут ко мне, по названию игры.

        Args:
            game_name (str): название игры.

        Returns:
            List[Record]: список записей игры в пути ко мне.
        """
        try:
            return await self.repo.get_by_game(game_name, RecordStatus.IN_TRANSIT_TO_ME)
        except Exception:
            logger.exception("Error getting in transit to me records by game")
            raise

    # Read by identifiers

    async def get_by_bulk_order_id(self, order_id: int) -> List[Record]:
        """Получает записи, связанные с оптовым заказом.

        Args:
            order_id (int): id оптового заказа.

        Returns:
            List[Record]: список записей оптового заказа.
        """
        try:
            return await self.repo.get_by_bulk_order_id(order_id)
        except Exception:
            logger.exception("Error getting records by bulk order id")
            raise

    async def get_by_id_with_relations(self, item_id: int) -> Optional[Record]:
        """Получает запись по id с загруженными связями (игра и транзакция).

        Args:
            item_id (int): id записи.

        Returns:
            Optional[Record]: запись со связями или None, если запись не найдена.
        """
        try:
            return await self.repo.get_by_id_with_relations(item_id)
        except Exception:
            logger.exception("Error getting record by id with relations")
            raise

    async def get_many_by_ids_with_relations(
        self,
        record_ids: List[int],
    ) -> List[Record]:
        """Получает несколько записей со всеми связями одним запросом.

        Args:
            record_ids (List[int]): список id записей.

        Returns:
            List[Record]: список записей со связями.
        """
        try:
            return await self.repo.get_many_by_ids_with_relations(record_ids)
        except Exception:
            logger.exception("Error getting records by ids with relations")
            raise

    # Price operations

    async def get_price_selling_for_game_in_available(self, game_name: str) -> int:
        """Получает цену продажи для конкретной игры из наличия.

        Args:
            game_name (str): название игры.

        Returns:
            int: цена продажи или 0, если цена не установлена.
        """
        try:
            return await self.repo.get_price_selling_for_game_in_available(game_name)
        except Exception:
            logger.exception("Error getting price selling for game in available")
            raise

    async def get_prices_selling_for_games_in_available(self, game_names: list[str]) -> dict[int, int]:
        """Получает цены продажи для списка игр из наличия.

        Args:
            game_names (list[str]): список названий игр.

        Returns:
            dict[int, int]: цены продажи в формате {game_id: price_selling}.
        """
        try:
            return await self.repo.get_prices_selling_for_games_in_available(game_names)
        except Exception:
            logger.exception("Error getting prices selling for games in available")
            raise

    # Updates

    async def update_price_selling_for_games(self, game_name: str, new_price: int) -> int:
        """Обновляет цену продажи для всех доступных записей игры.

        Args:
            game_name (str): название игры.
            new_price (int): новая цена продажи.

        Returns:
            int: количество обновлённых записей.
        """
        try:
            rowscount = await self.repo.update_price_selling_for_games(game_name, new_price)

            if rowscount == 0:
                logger.warning("Available records for game not found")

            return rowscount
        except Exception:
            logger.exception("Error updating price selling for games")
            raise