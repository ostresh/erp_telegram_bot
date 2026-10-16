from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
import logging

from app.core.db.repository import RecordRepository
from app.core.dto.reports.sales import (
    SalesPeriodReport,
    SalesGameItem,
    MovementReport,
    MovementItem,
)
from app.core.service.excel_export import (
    SalesReportExcelExporter,
    MovementReportExcelExporter,
)
from app.core.db.statuses import RecordStatus

logger = logging.getLogger(__name__)


class SalesService:
    """
    Сервис для отчетов по продажам и движению товаров.

    Предоставляет два основных отчета:
    - Отчет по продажам за период (агрегаты считает БД через GROUP BY)
    - Отчет по движению товаров за период (полный список с расшифровкой)
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация сервиса.

        Args:
            session: Активная сессия БД из UnitOfWork
        """
        self.repo = RecordRepository(session)

    async def get_sales_report(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> SalesPeriodReport:
        """
        Отчет по продажам за указанный период.

        Все агрегаты по играм считает БД одним запросом с GROUP BY.
        Сервис только маппит проекцию в DTO отчета и суммирует
        уже агрегированные строки по играм для итоговых метрик.

        Args:
            period_start (datetime): Начало периода (включительно)
            period_end (datetime): Конец периода (включительно)

        Returns:
            SalesPeriodReport с итогами и детализацией по играм

        Raises:
            Exception: При ошибке получения данных
        """
        logger.info(f"Generating sales period report [{period_start}, {period_end}]")

        # Один запрос. На выходе — по одной строке на игру,
        # а не тысячи ORM-объектов Record.
        stats = await self.repo.get_sales_grouped_by_game(
            period_start,
            period_end,
        )

        # avg_price_per_unit посчитается сам в __post_init__ SalesGameItem
        sales_by_game = [
            SalesGameItem(
                game_name=row.game_name,
                sold_count=row.sold_count,
                total_revenue=row.total_revenue,
                total_profit=row.total_profit,
            )
            for row in stats
        ]

        # Суммируем агрегаты по играм, а не сырые записи.
        # Количество строк = количество уникальных проданных игр.
        report = SalesPeriodReport(
            period_start=period_start,
            period_end=period_end,
            total_sold_count=sum(row.sold_count for row in stats),
            total_revenue=sum(row.total_revenue for row in stats),
            total_purchase_cost=sum(row.total_purchase_cost for row in stats),
            total_profit=sum(row.total_profit for row in stats),
            sales_by_game=sales_by_game,
        )

        logger.info(
            f"Sales period report generated: "
            f"sold_count={report.total_sold_count}, "
            f"revenue={report.total_revenue}, "
            f"profit={report.total_profit}, "
            f"games={len(sales_by_game)}"
        )

        return report

    async def get_movement_report(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> MovementReport:
        """
        Отчет по движению товаров за период.

        Возвращает список всех записей, которые были куплены или
        проданы в указанный период, с расшифровкой названий игр
        и транзакций, прибылью по каждой позиции (через Record.profit),
        а также сводную статистику по статусам.

        Args:
            period_start (datetime): Начало периода (включительно)
            period_end (datetime): Конец периода (включительно)

        Returns:
            MovementReport со списком товаров и статистикой

        Raises:
            Exception: При ошибке получения данных
        """
        logger.info(f"Generating movement report [{period_start}, {period_end}]")

        try:
            # Получаем записи с движением в период (купленные или проданные)
            records = await self.repo.get_records_with_movement_in_period(
                period_start,
                period_end,
            )

            # Конвертируем в DTO
            items: List[MovementItem] = []
            sold_count = 0
            available_count = 0
            in_transit_to_client_count = 0
            in_transit_to_me_count = 0

            for record in records:
                # Создаем MovementItem из Record
                item = MovementItem(
                    id=record.id,
                    game_name=record.game.name if record.game else None,
                    utility_title=record.utility.title if record.utility else None,
                    bulk_order_id=record.bulk_order_id,
                    purchase_at=record.purchase_at,
                    sold_at=record.sold_at,
                    price_purchase=record.price_purchase,
                    price_selling=record.price_selling,
                    price_sold=record.price_sold,
                    status=record.status,
                    swap=record.swap,
                    reserve=record.reserve,
                    comment=record.comment,
                    profit=record.profit,
                )
                items.append(item)

                # Считаем статистику по статусам
                if record.status == RecordStatus.SOLD.value:
                    sold_count += 1
                elif record.status == RecordStatus.AVAILABLE.value:
                    available_count += 1
                elif record.status == RecordStatus.IN_TRANSIT_TO_CLIENT.value:
                    in_transit_to_client_count += 1
                elif record.status == RecordStatus.IN_TRANSIT_TO_ME.value:
                    in_transit_to_me_count += 1

            # Создаем отчет
            report = MovementReport(
                period_start=period_start,
                period_end=period_end,
                items=items,
                total_purchases=len(records),
                sold_count=sold_count,
                available_count=available_count,
                in_transit_to_client_count=in_transit_to_client_count,
                in_transit_to_me_count=in_transit_to_me_count,
            )

            logger.info(
                f"Movement report generated: "
                f"total={report.total_purchases}, "
                f"sold={report.sold_count}, "
                f"available={report.available_count}"
            )

            return report

        except Exception as e:
            logger.exception(f"Error generating movement report: {e}")
            raise
        
    async def export_sales_report_to_excel(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> bytes:
        """Экспортирует отчет по продажам за период в Excel."""
        report = await self.get_sales_report(period_start, period_end)
        return SalesReportExcelExporter().export(report)

    async def export_movement_report_to_excel(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> bytes:
        """Экспортирует отчет по движению товаров за период в Excel."""
        report = await self.get_movement_report(period_start, period_end)
        return MovementReportExcelExporter().export(report)