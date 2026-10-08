from typing import NamedTuple

class ExpensesIncomesDTO(NamedTuple):
    """
    DTO базовых финансовых показателей: расходы и доходы.

    Расходы — сумма всех закупочных цен.
    Доходы — сумма цен продажи по записям со статусами
    «Продан», «Едет ко мне», «Едет к покупателю».
    Значения никогда не бывают отрицательными или пустыми:
    при отсутствии данных возвращается 0 (через COALESCE).

    Возвращается методом:
        RecordRepository.get_expenses_incomes_financials

    Attributes:
        expenses: общая сумма расходов (закупок), по умолчанию 0
        incomes: общая сумма доходов (продаж), по умолчанию 0
    """
    expenses: int
    incomes: int


class SalesFinancialsDTO(NamedTuple):
    """
    DTO выручки и количества проданных дисков.

    Выручка — «грязная» разница доходов и расходов по играм
    (цена продажи минус цена покупки) со статусами
    «Продан» и «Едет к покупателю».
    Количество проданных дисков — только игры, без транзакций.

    Возвращается методом:
        RecordRepository.get_sales_financials

    Attributes:
        revenue: суммарная выручка по играм (доходы − расходы)
        discs_count_sold: количество проданных дисков (без транзакций)
    """
    revenue: int
    discs_count_sold: int


class InTransitToClientDTO(NamedTuple):
    """
    DTO суммарных показателей записей, едущих к покупателю.

    Агрегирует сумму и количество одним запросом,
    так как у них одинаковое условие фильтрации
    (статус «Едет к покупателю», только игры).

    Возвращается методом:
        RecordRepository.get_in_transit_to_client_financial

    Attributes:
        on_way: суммарная цена продажи записей в пути к покупателю
        on_way_count: количество записей, едущих к покупателю
    """
    on_way: int
    on_way_count: int


class AssetsValueDTO(NamedTuple):
    """
    DTO стоимости товаров в наличии и едущих ко мне.

    Для каждой записи берётся цена продажи, если она задана,
    иначе — цена покупки. Суммы считаются отдельно для статусов
    «В наличии» и «Едет ко мне».

    Возвращается методом:
        RecordRepository.get_assets_value

    Attributes:
        available_sum: суммарная стоимость товаров в наличии
        coming_to_me_sum: суммарная стоимость товаров, едущих ко мне
    """
    available_sum: int
    coming_to_me_sum: int