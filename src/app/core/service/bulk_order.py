from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json

from app.core.db.repository import BulkOrderRepository
from app.core.db.models import BulkOrder, Game, Record
from app.core.db.statuses.bulk_order import BulkOrderStatus
from app.core.db.statuses.record import RecordStatus
from app.core.dto import BulkOrderJsonDTO
from app.core.service.base import BaseService
from app.core.service.game import GameService
from app.core.service.record import RecordService

import logging

logger = logging.getLogger(__name__)

class BulkOrderService(BaseService[BulkOrder, BulkOrderRepository]):
    """Сервис для работы с BulkOrder"""
    
    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session, BulkOrderRepository(session))
        self.record_service = RecordService(session)
        self.game_service = GameService(session)
        
    async def get_created(self) -> List[BulkOrder]:
        """
        Получение всех созданных оптовых заказов
        
        Return:
            Список BulkOrder
        
        Raises:
            Exception: При ошибке создания
        """
        
        logger.info("Getting delivery to me bulk orders")
                
        try:
            return await self.repo.get_created()
        except Exception as e:
            logger.exception(f"Error get delivery to me bulk orders: {e}")
            raise
        
    async def get_in_transit(self) -> List[BulkOrder]:
        """
        Получение всех оптовых заказов
        Которые едут ко мне
        
        Return:
            Список BulkOrder
        
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.info("Getting in transit to me bulk orders")
                        
        try:
            return await self.repo.get_in_transit()
        except Exception as e:
            logger.exception(f"Error get in transit to me bulk orders: {e}")
            raise
        
    async def create_from_json(self, json_text: str) -> BulkOrder:
        """
        Создание оптового заказа из JSON.
        Также создаются связанные Record.
        
        Формат входного JSON:
        {
            "seller": "Pulse",
            "items": [
                {"game_name": "Ghost of Tsushima", "count": 4, "price_purchase": 2300},
                {"game_name": "Saros", "count": 5, "price_purchase": 3400}
            ]
        }
        """
        
        dto = BulkOrderJsonDTO.model_validate_json(json_text)
        
        games_map = await self._load_games_map(dto.unique_game_names)
        prices_map = await self.record_service.get_prices_selling_for_games_in_available(dto.unique_game_names)
        
        new_bulk_order = await self.create(
            BulkOrder(
                seller=dto.seller,
                order_status=BulkOrderStatus.CREATED.value,
                total_count=dto.total_count,
                total_cost=dto.total_cost,
            )
        )
        
        await self._create_records(dto.items, new_bulk_order.id, games_map, prices_map)
        
        logger.info(
            f"Bulk order #{new_bulk_order.id} created: "
            f"{len(dto.items)} positions, {dto.total_count} discs, "
            f"total_cost={dto.total_cost}"
        )
        return new_bulk_order
        
    async def _load_games_map(self, names: list[str]) -> dict[str, Game]:
        """
        Батчевая загрузка игр
        
        Args:
            names (list[str]): список названий игр
            
        Returns:
            dict[str, Game]
        """
        games = await self.game_service.get_by_names(names)
        games_map = {game.name: game for game in games}
        
        missing = set(names) - set(games_map.keys())
        if missing:
            raise ValueError(f"Игры не найдены в базе: {', '.join(missing)}")
        
        return games_map
    
    async def _create_records(
        self,
        items: list,
        bulk_order_id: int,
        games_map: dict,
        prices_map: dict[str, int],
    ) -> None:
        """
        Массовое создание записей (Record) для оптового заказа.
        
        Для каждой позиции из списка создаётся количество записей,
        равное полю ``count``. Каждая запись привязывается к оптовому
        заказу через ``bulk_order_id`` и к игре через ``game_id``.
        
        Цена продажи берётся из ``prices_map`` по имени игры.
        Если цена для игры не найдена, устанавливается 0.
        Все записи создаются со статусом ``AVAILABLE``.
        
        Args:
            items: Список позиций оптового заказа (из входного JSON).
            bulk_order_id: ID созданного оптового заказа.
            games_map: Маппинг {имя игры: объект Game} для получения ``game_id``.
            prices_map: Маппинг {имя игры: цена продажи} для установки ``price_selling``.
            
        Returns:
            None
            
        Raises:
            Exception: При ошибке массового создания записей в БД.
        """
        
        records = []
        
        for item in items:
            game = games_map[item.game_name]
            selling_price = prices_map.get(game.id, 0)
            
            for _ in range(item.count):
                records.append(Record(
                    game_id=game.id,
                    bulk_order_id=bulk_order_id,
                    price_purchase=item.price_purchase,
                    price_selling=selling_price,
                    status=RecordStatus.IN_TRANSIT_TO_ME.value,
                ))
        
        await self.record_service.create_many(records)
        logger.debug(f"Created {len(records)} records for bulk order #{bulk_order_id}")
        
    async def add_delivery_cost(
        self,
        bulk_order_id: int,
        delivery_cost: int,
    ) -> BulkOrder:
        """
        Проставляет стоимость доставки оптового заказа и распределяет её
        между связанными записями.

        Выполняется в одной сессии (одна транзакция): обновление заказа
        и всех его записей коммитится один раз, поэтому частичного
        применения не будет.

        Стоимость доставки делится поровну между записями, остаток от
        деления распределяется по первым записям. Найденная часть
        прибавляется к ``price_purchase`` каждой записи.

        Побочные эффекты:
            - меняет ``delivery_cost`` и ``order_status`` оптового заказа
            - увеличивает ``price_purchase`` связанных записей

        Args:
            bulk_order_id: id оптового заказа
            delivery_cost: стоимость доставки

        Returns:
            BulkOrder: обновлённый оптовый заказ

        Raises:
            ValueError: если у оптового заказа нет записей
        """
        
        records = await self.record_service.get_by_bulk_order_id(bulk_order_id)
        
        if not records:
            raise ValueError(f"У оптового заказа #{bulk_order_id} нет записей")
        
        delivery_parts = self._split_price_evenly(delivery_cost, len(records))
        
        for record, delivery_part in zip(records, delivery_parts):
            await self.record_service.update(
                record.id,
                price_purchase=(record.price_purchase or 0) + delivery_part,
            )
        
        u_bulk_order = await self.update(
            bulk_order_id,
            delivery_cost=delivery_cost,
            order_status=BulkOrderStatus.IN_TRANSIT.value,
        )
        
        logger.info(
            f"Bulk order #{bulk_order_id}: delivery cost {delivery_cost} "
            f"distributed across {len(records)} records"
        )
        
        return u_bulk_order
    
    async def complete_arrival(self, bulk_order_id: int) -> BulkOrder:
        """
        Завершает прибытие оптового заказа: помечает заказ как завершённый
        и переводит связанные записи в наличие с актуальной ценой продажи.

        Выполняется в одной сессии (одна транзакция): обновление заказа
        и всех его записей коммитится один раз, поэтому частичного
        применения не будет.

        Цена продажи для каждой записи берётся из цен наличия по её игре
        (если для игры цен нет — устанавливается 0).

        Побочные эффекты:
            - меняет ``order_status`` и ``arrived_at`` оптового заказа
            - меняет ``status`` и ``price_selling`` связанных записей

        Args:
            bulk_order_id: id оптового заказа

        Returns:
            BulkOrder: обновлённый оптовый заказ
        """
        
        records = await self.record_service.get_by_bulk_order_id(bulk_order_id)
        
        game_ids = {record.game_id for record in records if record.game_id is not None}
        
        prices_map: dict[int, int] = {}
        if game_ids:
            games = await self.game_service.get_by_ids(list(game_ids))
            prices_map = await self.record_service.get_prices_selling_for_games_in_available(
                [game.name for game in games],
            )
        
        for record in records:
            await self.record_service.update(
                record.id,
                price_selling=prices_map.get(record.game_id, 0),
                status=RecordStatus.AVAILABLE.value,
            )
        
        u_bulk_order = await self.update(
            bulk_order_id,
            order_status=BulkOrderStatus.COMPLETED.value,
            arrived_at=datetime.now(timezone.utc),
        )
        
        logger.info(
            f"Bulk order #{bulk_order_id} completed: "
            f"{len(records)} records moved to available"
        )
        
        return u_bulk_order
    
    @staticmethod
    def _split_price_evenly(price: int, parts_count: int) -> List[int]:
        """
        Разделяет цену по частям.
        
        Args:
            price (int): цена
            parts_count (int): количество частей
            
        Returns:
            Список с ценами
        
        Raises:
            ValueError: если количество частей меньше 1
        """
        
        if parts_count < 1:
            raise ValueError('Количество частей должно быть не меньше 1')

        base, remainder = divmod(price, parts_count)

        return [base + 1 if i < remainder else base for i in range(parts_count)]
        
    async def get_many_by_ids(
        self,
        order_ids: List[int],
    ) -> List[BulkOrder]:
        """
        Получает несколько записей со всеми связями одним запросом.

        Использует IN для фильтрации и selectinload для жадной
        загрузки связей, что минимизирует количество запросов к БД.

        Args:
            record_ids: список id записей

        Returns:
            List[Record]: список записей со связями
        """
        
        logger.info("Getting BulkOrder by ids={order_ids}")
                        
        try:
            return await self.repo.get_many_by_ids(order_ids)
        except Exception as e:
            logger.exception(f"Error getting BulkOrder by ids={order_ids}: {e}")
            raise