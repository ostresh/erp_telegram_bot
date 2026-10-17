from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

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

    # Инициализация

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session, BulkOrderRepository(session))
        self.record_service = RecordService(session)
        self.game_service = GameService(session)

    # Получение списков

    async def get_created(self) -> List[BulkOrder]:
        """Получает все созданные оптовые заказы.

        Returns:
            List[BulkOrder]: список оптовых заказов в статусе CREATED.
        """
        try:
            return await self.repo.get_by_status(status=BulkOrderStatus.CREATED)
        except Exception:
            logger.exception("Error getting created bulk orders")
            raise

    async def get_in_transit(self) -> List[BulkOrder]:
        """Получает все оптовые заказы, которые едут ко мне.

        Returns:
            List[BulkOrder]: список оптовых заказов в статусе IN_TRANSIT.
        """
        try:
            return await self.repo.get_by_status(status=BulkOrderStatus.IN_TRANSIT)
        except Exception:
            logger.exception("Error getting in transit to me bulk orders")
            raise

    # Создание и изменение

    async def create_from_json(self, json_text: str) -> BulkOrder:
        """Создаёт оптовый заказ из JSON вместе со связанными записями.

        Формат входного JSON:
        {
            "seller": "Pulse",
            "items": [
                {"game_name": "Ghost of Tsushima", "count": 4, "price_purchase": 2300},
                {"game_name": "Saros", "count": 5, "price_purchase": 3400}
            ]
        }

        Args:
            json_text (str): JSON-строка с данными оптового заказа.

        Returns:
            BulkOrder: созданный оптовый заказ.
        """
        try:
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

            return new_bulk_order
        except Exception:
            logger.exception("Error creating bulk order from json")
            raise
        
    async def add_delivery_cost(
        self,
        bulk_order_id: int,
        delivery_cost: int,
    ) -> BulkOrder:
        """Проставляет стоимость доставки и распределяет её между записями заказа.

        Стоимость доставки делится поровну между записями, остаток от деления
        распределяется по первым записям и прибавляется к ``price_purchase``.
        Обновление заказа и его записей выполняется в одной транзакции.

        Args:
            bulk_order_id (int): id оптового заказа.
            delivery_cost (int): стоимость доставки.

        Returns:
            BulkOrder: обновлённый оптовый заказ.
        """
        try:
            records = await self.record_service.get_by_bulk_order_id(bulk_order_id)

            if not records:
                raise ValueError(f"Bulk order #{bulk_order_id} dont have records")

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

            return u_bulk_order
        except Exception:
            logger.exception("Error adding delivery cost to bulk order")
            raise

    async def complete_arrival(self, bulk_order_id: int) -> BulkOrder:
        """Завершает прибытие заказа и переводит связанные записи в наличие.

        Заказ помечается завершённым, а связанные записи переводятся в наличие
        с актуальной ценой продажи по их игре (если цен нет — устанавливается 0).
        Обновление заказа и его записей выполняется в одной транзакции.

        Args:
            bulk_order_id (int): id оптового заказа.

        Returns:
            BulkOrder: обновлённый оптовый заказ.
        """
        try:
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

            return u_bulk_order
        except Exception:
            logger.exception("Error completing bulk order arrival")
            raise

    async def delete(self, bulk_order_id: int) -> bool:
        """Удаляет оптовый заказ вместе со связанными записями.

        Args:
            bulk_order_id (int): id оптового заказа.

        Returns:
            bool: True, если заказ и все его записи удалены.
        """
        try:
            results = []

            records = await self.record_service.get_by_bulk_order_id(bulk_order_id)

            results.append(await self.record_service.delete_by_ids(
                [record.id for record in records]
                )
            )

            results.append(await self.repo.delete(bulk_order_id))

            return all(results)
        except Exception:
            logger.exception("Error deleting bulk order")
            raise

    # Получение по идентификаторам

    async def get_many_by_ids(
        self,
        order_ids: List[int],
    ) -> List[BulkOrder]:
        """Получает несколько оптовых заказов по списку id одним запросом.

        Args:
            order_ids (List[int]): список id оптовых заказов.

        Returns:
            List[BulkOrder]: список найденных оптовых заказов.
        """
        try:
            return await self.repo.get_many_by_ids(order_ids)
        except Exception:
            logger.exception("Error getting bulk orders by ids")
            raise

    async def get_by_id_with_relations(self, item_id: int) -> Optional[BulkOrder]:
        """Получает оптовый заказ по id с загруженными связями (записи).

        Args:
            item_id (int): id оптового заказа.

        Returns:
            Optional[BulkOrder]: оптовый заказ со связями или None, если не найден.
        """
        try:
            return await self.repo.get_by_id_with_relations(item_id)
        except Exception:
            logger.exception("Error getting bulk order by id with relations")
            raise

    # Вспомогательные методы

    async def _load_games_map(self, names: list[str]) -> dict[str, Game]:
        """Загружает игры по списку названий в виде маппинга.

        Args:
            names (list[str]): список названий игр.

        Returns:
            dict[str, Game]: маппинг {название игры: объект Game}.
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
        """Массово создаёт записи (Record) для оптового заказа.

        Для каждой позиции создаётся количество записей, равное полю ``count``.
        Каждая запись привязывается к заказу через ``bulk_order_id`` и к игре
        через ``game_id``. Цена продажи берётся из ``prices_map`` по id игры
        (если цены нет — 0). Все записи создаются со статусом
        ``IN_TRANSIT_TO_ME``.

        Args:
            items (list): список позиций оптового заказа из входного JSON.
            bulk_order_id (int): id созданного оптового заказа.
            games_map (dict): маппинг {название игры: объект Game}.
            prices_map (dict[str, int]): маппинг {id игры: цена продажи}.

        Returns:
            None
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

    @staticmethod
    def _split_price_evenly(price: int, parts_count: int) -> List[int]:
        """Делит цену на части, распределяя остаток по первым частям.

        Args:
            price (int): цена.
            parts_count (int): количество частей.

        Returns:
            List[int]: список цен по частям.
        """
        if parts_count < 1:
            raise ValueError('Количество частей должно быть не меньше 1')

        base, remainder = divmod(price, parts_count)

        return [base + 1 if i < remainder else base for i in range(parts_count)]
        