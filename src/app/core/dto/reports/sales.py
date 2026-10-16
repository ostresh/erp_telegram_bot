from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from app.core.db.statuses.record import RecordStatus

@dataclass(frozen=True)
class GameSalesStats:
    """
    Проекция агрегированных продаж по одной игре.

    Формируется репозиторием через GROUP BY.
    Одна экземпляр = одна игра за выбранный период.
    """

    game_name: str
    sold_count: int
    total_revenue: int
    total_purchase_cost: int
    total_profit: int

@dataclass
class SalesGameItem:
    """
    Статистика продаж по конкретной игре за период.
    
    Attributes:
        game_name: Название игры
        sold_count: Количество проданных единиц этой игры
        total_revenue: Общая выручка по игре (сумма price_sold)
        total_profit: Общая прибыль по игре (сумма record.profit)
        avg_price_per_unit: Средняя цена продажи одной единицы
    """
    
    game_name: str
    sold_count: int = 0
    total_revenue: int = 0
    total_profit: int = 0
    avg_price_per_unit: int = 0
    
    def __post_init__(self) -> None:
        """Вычисление средней цены за единицу"""
        self.avg_price_per_unit = (
            self.total_revenue // self.sold_count 
            if self.sold_count > 0 else 0
        )


@dataclass
class SalesPeriodReport:
    """
    Отчет по продажам за определенный период.
    
    Attributes:
        period_start: Начало периода (включительно)
        period_end: Конец периода (включительно)
        total_sold_count: Общее количество проданных товаров
        total_revenue: Общая выручка (сумма price_sold)
        total_purchase_cost: Общая себестоимость (сумма price_purchase)
        total_profit: Общая прибыль (сумма record.profit)
        avg_profit_per_item: Средняя прибыль на один проданный товар
        sales_by_game: Детализация продаж по каждой игре
    """
    
    period_start: datetime
    period_end: datetime
    total_sold_count: int = 0
    total_revenue: int = 0
    total_purchase_cost: int = 0
    total_profit: int = 0
    avg_profit_per_item: int = 0
    sales_by_game: List[SalesGameItem] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Вычисление зависимых полей после инициализации"""
        
        # Средняя прибыль на товар (защита от деления на ноль)
        self.avg_profit_per_item = (
            self.total_profit // self.total_sold_count 
            if self.total_sold_count > 0 else 0
        )


@dataclass
class MovementItem:
    """
    Элемент отчета по движению товаров.
    
    Содержит все поля Record, кроме game_id и util_id,
    которые заменены на читаемые названия (game_name, utility_title).
    Прибыль по позиции берётся из свойства Record.profit.
    """
    
    id: int
    game_name: Optional[str] = None
    utility_title: Optional[str] = None
    bulk_order_id: Optional[int] = None
    purchase_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None
    price_purchase: Optional[int] = None
    price_selling: Optional[int] = None
    price_sold: Optional[int] = None
    status: Optional[str] = None
    swap: Optional[str] = None
    reserve: Optional[str] = None
    comment: Optional[str] = None
    profit: Optional[int] = None
    
    @property
    def status_display(self) -> str:
        """Человекочитаемое (русское) название статуса."""
        if self.status is None:
            return ""
        try:
            return RecordStatus(self.status).display_name
        except (ValueError, KeyError):
            # если прилетело неизвестное значение — не падаем, отдаём как есть
            return str(self.status)


@dataclass
class MovementReport:
    """
    Отчет по движению товаров (покупки и продажи) за период.
    
    Показывает все записи, которые были куплены или проданы
    в указанный период.
    
    Attributes:
        period_start: Начало периода (включительно)
        period_end: Конец периода (включительно)
        items: Список всех записей с расшифровкой названий
        total_purchases: Общее количество записей в отчете
        sold_count: Количество проданных товаров
        available_count: Количество товаров в наличии
        in_transit_to_client_count: Количество товаров, едущих к покупателю
        in_transit_to_me_count: Количество товаров, едущих ко мне
    """
    
    period_start: datetime
    period_end: datetime
    items: List[MovementItem] = field(default_factory=list)
    total_purchases: int = 0
    sold_count: int = 0
    available_count: int = 0
    in_transit_to_client_count: int = 0
    in_transit_to_me_count: int = 0