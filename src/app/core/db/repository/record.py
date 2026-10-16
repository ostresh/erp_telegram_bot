from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, exists, func, and_
from sqlalchemy.orm import selectinload

from app.core.db.models import Record, Game
from app.core.db.repository.base import BaseRepository
from app.core.db.statuses import RecordStatus
from app.core.dto import AvailableRecordDTO

import logging

logger = logging.getLogger(__name__)

class RecordRepository(BaseRepository[Record]):
    """Репозиторий для Record. Наследует базовые CRUD, добавляет специфичные методы"""

    # Инициализация

    def __init__(self, session: AsyncSession):
        super().__init__(session, Record)

    # Проверки

    async def is_game_available(self, game_name: str) -> bool:
        """
        Проверка, есть ли игра в наличии
        
        Args:
            game_name (str): название игры

        Returns:
            bool: есть ли игра в наличии
        """
        logger.debug(f"Checking availability for game '{game_name}'")
        
        stmt = select(
            exists(
                select(Record.id)
                .join(Game, Record.game_id == Game.id)
                .where(
                    Game.name == game_name,
                    Record.status == RecordStatus.AVAILABLE.value
                )
            )
        )
        result = await self.session.execute(stmt)
        available = result.scalars().first()
            
        logger.debug(f"Game '{game_name}' available: {available}")
        return available

    # Получение записей по состоянию

    async def get_available(self) -> List[AvailableRecordDTO]:
        """
        Получение всех игр из наличия с группировкой по играм

        Args:
            Отсутствуют

        Returns:
            List[AvailableRecordDTO]: Record и Game.name
        """
        logger.debug("Getting available records")
        
        stmt = (
            select(
                Record,
                Game.name.label('game_name')
            )
            .join(Game, Record.game_id == Game.id)
            .where(Record.status == RecordStatus.AVAILABLE.value)
            .group_by(Record.id, Game.name)
            .order_by(Record.id)
        )
            
        rows = (await self.session.execute(stmt)).all()
        records = [
            AvailableRecordDTO(
                record=row.Record,
                game_name=row.game_name
            )
            for row in rows
        ]
            
        logger.debug(f"Retrieved {len(records)} available records")
        return records

    async def get_in_transit_to_me(self) -> List[Record]:
        """
        Получение всех записей, которые едут ко мне

        Args:
            Отсутствуют

        Returns:
            List[Record]: Список Record
        """
        logger.debug("Getting delivery to me records")

        stmt = (
            select(Record)
            .where(
                Record.status == RecordStatus.IN_TRANSIT_TO_ME.value
            )
            .order_by(Record.id.asc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        logger.debug(f"Retrieved {len(records)} delivery to me records")
        return records

    async def get_in_transit_to_client(self) -> List[Record]:
        """
        Получение всех записей, которые едут к покупателю

        Args:
            Отсутствуют

        Returns:
            List[Record]: Список Record
        """
        logger.debug("Getting delivery to client records")

        stmt = (
            select(Record)
            .where(
                Record.status == RecordStatus.IN_TRANSIT_TO_CLIENT.value
            )
            .order_by(Record.id.asc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        logger.debug(f"Retrieved {len(records)} delivery to client records")
        return records

    # Получение записей по игре

    async def get_by_game(
        self, 
        game_name: str, 
        status: Optional[RecordStatus] = None
    ) -> List[Record]:
        """
        Получение списка Record по определенной Game с фильтрацией по статусу

        Args:
            game_name (str): название игры
            status (Optional[RecordStatus]): Статус для фильтрации

        Returns:
            List[Record]: Список Record
        """
        logger.debug(f"Getting records by game: {game_name}")
        
        stmt = (
            select(Record)
            .join(Game, Record.game_id == Game.id)
            .where(Game.name == game_name)
            .order_by(Record.id.asc())
        )

        if status:
            stmt = stmt.where(Record.status == status.value)

        result = await self.session.execute(stmt)
        records = result.scalars().all()

        logger.debug(f"Retrieved {len(records)} records for game: {game_name}")
        return records

    # Получение по идентификаторам

    async def get_by_bulk_order_id(self, order_id: int) -> List[Record]:
        """
        Получение всех записей, связанных с оптовым заказом

        Args:
            order_id (int): id оптового заказа

        Returns:
            List[Record]: Список Record
        """
        logger.debug(f"Getting records for bulk order id={order_id}")
        
        stmt = (
            select(Record)
            .where(Record.bulk_order_id == order_id)
            .order_by(Record.id.asc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        logger.debug(f"Retrieved {len(records)} records for bulk order id={order_id}")
        return records

    async def get_by_id_with_relations(self, item_id: int) -> Optional[Record]:
        """
        Получение записи по id с загруженными связями (игра и транзакция)

        Args:
            item_id (int): id записи

        Returns:
            Optional[Record]: Объект Record с загруженными связями или None
        """
        logger.debug(f"Getting Record by id={item_id} with relations")
        
        stmt = (
            select(Record)
            .options(
                selectinload(Record.game),
                selectinload(Record.utility),
                selectinload(Record.bulk_order)
            )
            .where(Record.id == item_id)
        )
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
            
        logger.debug(f"Record with id={item_id} retrieval completed")
        return item

    async def get_many_by_ids_with_relations(
        self,
        record_ids: List[int],
    ) -> List[Record]:
        """
        Получение нескольких записей со всеми связями одним запросом

        Args:
            record_ids (List[int]): список id записей

        Returns:
            List[Record]: список записей со связями
        """
        logger.debug(f"Getting Records by ids={record_ids} with relations")
        
        if not record_ids:
            logger.debug(f"Records with ids={record_ids} not found")
            return []

        stmt = (
            select(Record)
            .options(
                selectinload(Record.game),
                selectinload(Record.utility),
                selectinload(Record.bulk_order),
            )
            .where(Record.id.in_(record_ids))
            .order_by(Record.id.asc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()
            
        logger.debug(f"Retrieved {len(records)} records by ids={record_ids}")
        return records

    # Цены продажи

    async def get_price_selling_for_game_in_available(self, game_name: str) -> int:
        """
        Получение цены продажи для конкретной игры из наличия
        
        Args:
            game_name (str): Название игры

        Returns:
            int: Максимальная цена для продажи или 0, если не установлена
        """
        logger.debug(f"Getting price_selling for game in available: {game_name}")
        
        stmt = (
            select(func.max(Record.price_selling))
            .join(Game, Record.game_id == Game.id)
            .where(
                and_(
                    Record.status == RecordStatus.AVAILABLE.value,
                    Game.name == game_name
                )
            )
        )
            
        result = await self.session.execute(stmt)
        price_selling = result.scalar_one_or_none()

        if price_selling is None:
            price_selling = 0

        logger.debug(f"Retrieved price_selling {price_selling} for game: {game_name}")
        return price_selling

    async def get_prices_selling_for_games_in_available(self, game_names: List[str]) -> dict[int, int]:
        """
        Получение цен для продажи для списка игр из наличия (максимальный прайс)

        Args:
            game_names (List[str]): Список названий игр

        Returns:
            dict[int, int]: {game_id: price_selling}
        """
        logger.debug(f"Getting prices_selling for games in available: {game_names}")

        stmt = (
            select(
                Record.game_id.label('game_id'),
                func.max(Record.price_selling).label('price')
            )
            .join(Game, Record.game_id == Game.id)
            .where(
                and_(
                    Record.status == RecordStatus.AVAILABLE.value,
                    Game.name.in_(game_names)
                )
            )
            .group_by(Record.game_id)
        )

        result = await self.session.execute(stmt)
        rows = result.all()
        prices = {row.game_id: row.price or 0 for row in rows}

        logger.debug(f"Retrieved {len(prices)} prices_selling for games: {game_names}")
        return prices

    # Обновления

    async def update_price_selling_for_games(self, game_name: str, new_price: int) -> int:
        """
        Обновление цены продажи для всех доступных записей игры

        Args:
            game_name (str): название игры
            new_price (int): цена

        Returns:
            int: количество изменённых строк
        """
        logger.debug(f"Updating price for game '{game_name}' to {new_price}")

        stmt = (
            update(Record)
            .where(
                Record.status == RecordStatus.AVAILABLE.value,
                Record.game_id.in_(
                    select(Game.id).where(Game.name == game_name)
                )
            )
            .values(price_selling=new_price)
        )

        result = await self.session.execute(stmt)
        await self.session.flush()
        count = result.rowcount

        logger.debug(f"Updated price for {count} records of game '{game_name}'")
        return count
