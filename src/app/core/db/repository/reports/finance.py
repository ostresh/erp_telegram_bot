from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_

from app.core.db.models import Record, Utility
from app.core.db.statuses import RecordStatus
from app.core.dto import (
    AssetsValueDTO,
    SalesFinancialsDTO,
    ExpensesIncomesDTO,
    InTransitToClientDTO,
)

import logging

logger = logging.getLogger(__name__)


class FinanceReportRepository:
    """Read-only репозиторий агрегатов финансового отчёта"""

    def __init__(self, session: AsyncSession):
        self.session = session

    # Доходы и расходы

    async def get_expenses_incomes_financials(self) -> ExpensesIncomesDTO:
        """
        Получить базовые доходы и расходы одним запросом

        Args:
            Отсутствуют

        Returns:
            ExpensesIncomesDTO: расходы (expenses) и доходы (incomes)
        """
        logger.debug("Getting expenses and incomes financials")

        stmt = select(
            # Расходы: сумма всех закупок
            func.coalesce(func.sum(Record.price_purchase), 0).label('expenses'),

            # Доходы: сумма продаж со статусами 'Продано', 'В пути ко мне', 'В пути к клиенту'
            func.coalesce(func.sum(
                case(
                    (Record.status.in_([
                        RecordStatus.SOLD.value,
                        RecordStatus.IN_TRANSIT_TO_ME.value,
                        RecordStatus.IN_TRANSIT_TO_CLIENT.value
                    ]), Record.price_sold),
                    else_=0
                )
            ), 0).label('incomes')
        )

        result = await self.session.execute(stmt)
        row = result.one()

        logger.debug(f"expenses={row.expenses}, incomes={row.incomes}")
        return ExpensesIncomesDTO(
            expenses=row.expenses,
            incomes=row.incomes
        )

    async def get_sales_financials(self) -> SalesFinancialsDTO:
        """
        Получить выручку по играм и количество проданных дисков одним запросом

        Выручка - грязная разница доходов и расходов по играм

        Args:
            Отсутствуют

        Returns:
            SalesFinancialsDTO: выручка (revenue) и количество проданных дисков (discs_count_sold)
        """
        logger.debug("Getting sales financials (revenue, discs_count_sold)")

        stmt = select(
            # Выручка: разница для игр (статусы 'Нет' и 'Едет к покупателю')
            func.coalesce(func.sum(
                case(
                    (and_(
                        Record.game_id.isnot(None),
                        Record.status.in_([
                            RecordStatus.SOLD.value,
                            RecordStatus.IN_TRANSIT_TO_CLIENT.value
                        ])
                    ),
                    func.coalesce(Record.price_sold, 0) - func.coalesce(Record.price_purchase, 0)),
                    else_=0
                )
            ), 0).label('revenue'),

            # Количество проданных дисков (только игры, без транзакций)
            func.count(
                case(
                    (and_(
                        Record.status == RecordStatus.SOLD.value,
                        Record.game_id.isnot(None),
                        Record.util_id.is_(None)
                    ), Record.id)
                )
            ).label('discs_count_sold')
        )

        result = await self.session.execute(stmt)
        row = result.one()

        logger.debug(f"Sales financials: revenue={row.revenue}, sold={row.discs_count_sold}")
        return SalesFinancialsDTO(
            revenue=row.revenue,
            discs_count_sold=row.discs_count_sold
        )

    # Стоимость активов и остатки

    async def get_assets_value(self) -> AssetsValueDTO:
        """
        Получить стоимость товаров в наличии и 'едет ко мне' одним запросом

        Берёт цену продажи, если она есть, иначе цену покупки

        Args:
            Отсутствуют

        Returns:
            AssetsValueDTO: стоимость товаров в наличии (available_sum) и едущих ко мне (coming_to_me_sum)
        """
        logger.debug("Getting assets value (available, coming_to_me)")

        # Цена: сначала продажная, иначе закупочная
        price = func.coalesce(Record.price_selling, Record.price_purchase)

        stmt = select(
            # Стоимость в наличии
            func.coalesce(func.sum(
                case(
                    (Record.status == RecordStatus.AVAILABLE.value, price),
                    else_=0
                )
            ), 0).label('available_sum'),

            # Стоимость 'едет ко мне'
            func.coalesce(func.sum(
                case(
                    (Record.status == RecordStatus.IN_TRANSIT_TO_ME.value, price),
                    else_=0
                )
            ), 0).label('coming_to_me_sum')
        )

        result = await self.session.execute(stmt)
        row = result.one()

        logger.debug(f"Assets: available={row.available_sum}, coming={row.coming_to_me_sum}")
        return AssetsValueDTO(
            available_sum=row.available_sum,
            coming_to_me_sum=row.coming_to_me_sum
        )

    async def count_available_discs(self) -> int:
        """
        Подсчитать количество дисков в наличии

        Args:
            Отсутствуют

        Returns:
            int: количество дисков со статусом 'Да'
        """
        logger.debug("Counting available discs")

        stmt = select(func.count(Record.id)).where(and_(
            Record.status == RecordStatus.AVAILABLE.value,
            Record.game_id.isnot(None),
            Record.util_id.is_(None)
            )
        )

        result = await self.session.execute(stmt)
        count = result.scalar_one()

        logger.debug(f"Available discs: {count}")
        return count

    async def get_in_transit_to_client_financial(self) -> InTransitToClientDTO:
        """
        Получить сумму и количество записей, едущих к покупателю

        Возвращает и сумму, и количество одним запросом, так как у них одинаковое условие фильтрации

        Args:
            Отсутствуют

        Returns:
            InTransitToClientDTO: сумма (on_way) и количество (on_way_count) записей, едущих к покупателю
        """
        logger.debug("Getting delivery to client (sum, count)")

        stmt = select(
            func.coalesce(func.sum(Record.price_sold), 0).label('on_way'),
            func.count(Record.id).label('on_way_count')
        ).where(
            and_(
                Record.status == RecordStatus.IN_TRANSIT_TO_CLIENT.value,
                Record.game_id.isnot(None)
            )
        )

        result = await self.session.execute(stmt)
        row = result.one()

        logger.debug(f"Delivery to client: sum={row.on_way}, count={row.on_way_count}")
        return InTransitToClientDTO(
            on_way=row.on_way,
            on_way_count=row.on_way_count
        )

    # Разбивка по транзакциям

    async def get_expenses_by_transaction(self, transaction_title: str) -> int:
        """
        Получить расходы по конкретной транзакции (например, Авито)

        Требует JOIN с таблицей utilities

        Args:
            transaction_title (str): название транзакции

        Returns:
            int: сумма расходов по транзакции
        """
        logger.debug(f"Getting expenses for transaction '{transaction_title}'")

        stmt = select(
            func.coalesce(func.sum(Record.price_purchase), 0)
        ).join(
            Utility, Record.util_id == Utility.id
        ).where(
            Utility.title.ilike(f'%{transaction_title}%')
        )

        result = await self.session.execute(stmt)
        expenses = result.scalar()

        logger.debug(f"Expenses for '{transaction_title}': {expenses}")
        return expenses
