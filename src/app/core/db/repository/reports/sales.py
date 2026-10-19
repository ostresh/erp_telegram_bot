from datetime import datetime, timedelta
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_, or_
from sqlalchemy.orm import selectinload

from app.core.db.models import Record, Game
from app.core.db.statuses import RecordStatus
from app.core.dto.reports.sales import GameSalesStats

import logging

logger = logging.getLogger(__name__)


class SalesReportRepository:
    """Read-only репозиторий отчётов по продажам и движению"""

    def __init__(self, session: AsyncSession):
        self.session = session

    # Агрегированные продажи

    async def get_sales_grouped_by_game(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> List[GameSalesStats]:
        """
        Агрегированные продажи по играм за период

        Одна строка результата = одна игра.
        Количество, выручка, себестоимость и прибыль считаются
        в БД через GROUP BY — ORM-объекты Record не материализуются.

        INNER JOIN с Game намеренно отсекает записи без игры
        (чистые транзакции / утилиты): они не являются продажами товара.

        Внутренне период — полуоткрытый интервал
        [period_start, period_end + 1 день): сравнение идёт строго «меньше»
        с границей на полуночи следующих суток. Так последний день входит
        в отчёт целиком, без ловушек с 23:59:59.999999.

        Args:
            period_start (datetime): Начало периода (включительно)
            period_end (datetime): Конец периода (включительно)

        Returns:
            List[GameSalesStats]: Список статистики, отсортированный по названию игры
        """
        logger.debug(
            f"Aggregating sales by game in period [{period_start}, {period_end}]"
        )

        # ВАЖНО: profit у Record — это Python-@property, в БД такой колонки нет.
        # Поэтому формула прибыли повторяется здесь на уровне SQL.
        # Держи её синхронизированной с Record.profit.
        profit_expr = case(
            (
                and_(
                    Record.price_sold.is_not(None),
                    Record.price_purchase.is_not(None),
                ),
                Record.price_sold - Record.price_purchase,
            ),
            (
                and_(
                    Record.price_sold.is_not(None),
                    Record.price_purchase.is_(None),
                ),
                Record.price_sold,
            ),
            (
                and_(
                    Record.price_sold.is_(None),
                    Record.price_purchase.is_not(None),
                ),
                -Record.price_purchase,
            ),
        )

        stmt = (
            select(
                Game.name.label("game_name"),
                func.count(Record.id).label("sold_count"),
                func.coalesce(func.sum(Record.price_sold), 0).label("total_revenue"),
                func.coalesce(func.sum(Record.price_purchase), 0).label("total_purchase_cost"),
                func.coalesce(func.sum(profit_expr), 0).label("total_profit"),
            )
            .join(Record.game)
            .where(
                Record.status.in_([
                    RecordStatus.SOLD.value, 
                    RecordStatus.IN_TRANSIT_TO_CLIENT.value
                ]),
                Record.sold_at >= period_start,
                Record.sold_at < period_end + timedelta(days=1),
            )
            .group_by(Game.id, Game.name)
            .order_by(Game.name.asc())
        )

        result = await self.session.execute(stmt)
        stats = [
            GameSalesStats(
                game_name=row.game_name,
                sold_count=row.sold_count,
                total_revenue=row.total_revenue,
                total_purchase_cost=row.total_purchase_cost,
                total_profit=row.total_profit,
            )
            for row in result.all()
        ]

        logger.debug(f"Retrieved {len(stats)} game sales stats in period")
        return stats

    # Детальное движение товаров

    async def get_records_with_movement_in_period(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> List[Record]:
        """
        Получить записи с движением в указанный период

        Выбирает записи, у которых дата покупки (purchase_at) ИЛИ
        дата продажи (sold_at) находятся в полуоткрытом интервале
        [period_start, period_end + 1 день). Это позволяет отследить
        все товары, которые были куплены или проданы в указанный период.

        Args:
            period_start (datetime): Начало периода (включительно)
            period_end (datetime): Конец периода (включительно)

        Returns:
            List[Record]: Список Record с движением в период
        """
        logger.debug(
            f"Getting records with movement in period [{period_start}, {period_end}]"
        )

        stmt = (
            select(Record)
            .options(
                selectinload(Record.game),
                selectinload(Record.utility),
            )
            .where(
                or_(
                    and_(
                        Record.purchase_at >= period_start,
                        Record.purchase_at < period_end + timedelta(days=1),
                    ),
                    and_(
                        Record.sold_at >= period_start,
                        Record.sold_at < period_end + timedelta(days=1),
                    ),
                )
            )
            .order_by(Record.id.asc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        logger.debug(f"Retrieved {len(records)} records with movement in period")
        return records
