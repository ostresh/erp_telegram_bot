from dataclasses import dataclass
from config import config


@dataclass
class FinanceReport:
    """Финансовый отчёт"""
    
    # входные данные из БД
    expenses: int = 0               # Расходы (все закупки)
    incomes: int = 0                # Доходы (все продажи)
    revenue: int = 0                # Грязная выручка по играм
    discs_count_sold: int = 0       # Продано дисков
    discs_count: int = 0            # Дисков в наличии
    on_way: int = 0                 # Едет к покупателю (сумма)
    available_sum: int = 0          # Сумма наличия
    on_way_count: int = 0           # Едет к покупателю (количество)
    coming_to_me_sum: int = 0       # Стоимость 'едет ко мне'
    avito_expenses: int = 0         # Расходы на Авито
    
    # поля из .env
    initial_balance: int = 0
    
    # вычисляемые поля
    net_profit: int = 0             # Чистая прибыль
    avg_revenue: int = 0            # Средняя выручка с диска
    on_account: int = 0             # На счету
    all_assets: int = 0             # Все активы
    
    def __post_init__(self) -> None:
        """Вычисление зависимых полей после инициализации"""
        
        # Чистая прибыль = доходы - расходы
        self.net_profit = self.incomes - self.expenses
        
        # Средняя выручка с диска (защита от деления на ноль)
        self.avg_revenue = (
            self.revenue // self.discs_count_sold 
            if self.discs_count_sold > 0 else 0
        )
        
        # На счету = чистая прибыль + начальный баланс + доп. средства
        self.on_account = (
            self.net_profit 
            + config.INITIAL_BALANCE
        )
        
        # Все активы = на счету + в пути + в наличии + едет ко мне
        self.all_assets = (
            self.on_account
            + self.on_way
            + self.available_sum
            + self.coming_to_me_sum
            + config.ALL_ASSETS
        )