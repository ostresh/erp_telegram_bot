from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.repository import RecordRepository
from app.core.service.finance.schemas import FinanceReport
import logging

from config import config

logger = logging.getLogger(__name__)

# Название транзакции Авито в таблице utilities
AVITO_TRANSACTION_TITLE = "[TRNS] Авито"


# Маппинг: какое поле какой группой запросов предоставляется
FIELD_GROUPS = {
    'expenses': 'base',
    'incomes': 'base',
    'revenue': 'sales',
    'discs_count_sold': 'sales',
    'avg_revenue': 'sales',
    'on_way': 'delivery',
    'on_way_count': 'delivery',
    'discs_count': 'available',
    'available_sum': 'assets',
    'coming_to_me_sum': 'assets',
    'all_assets': 'assets',
    'avito_expenses': 'avito',
    # Зависимые поля требуют базовые группы
    'net_profit': 'base',
    'on_account': 'base',
}


class FinanceService:
    """
    Сервис для расчёта финансовых показателей.
    
    Загружает только те группы данных, которые нужны
    для запрошенных полей отчёта.
    """
    
    def __init__(self, session: AsyncSession):
        self.repo = RecordRepository(session)
        self.config = config
    
    def _determine_groups(self, fields: list[str] | None) -> set[str]:
        """Определить, какие группы запросов нужны для полей"""
        if fields is None:
            return set(FIELD_GROUPS.values())
        return {FIELD_GROUPS[f] for f in fields if f in FIELD_GROUPS}
    
    async def get_report(self, fields: list[str] | None = None) -> FinanceReport:
        """
        Получить финансовый отчёт.
        
        Загружает только те группы данных, которые нужны
        для запрошенных полей. Зависимые поля вычисляются
        автоматически в FinanceReport.__post_init__.
        
        Данные берутся из DTO репозитория:
            ExpensesIncomesDTO, SalesFinancialsDTO,
            InTransitToClientDTO, AssetsValueDTO.
        
        Args:
            fields - список нужных полей (ключи FinanceReport).
                    None - загрузить всё.
        
        Return:
            FinanceReport с рассчитанными значениями
            
        Raises:
            Exception: При ошибке получения данных
        """
        logger.info(f"Generating finance report for fields: {fields}")
        
        try:
            groups = self._determine_groups(fields)
            data = {}
            
            # Загружаем только нужные группы
            if 'base' in groups:
                base = await self.repo.get_expenses_incomes_financials()
                data['expenses'] = base.expenses
                data['incomes'] = base.incomes
            
            if 'sales' in groups:
                sales = await self.repo.get_sales_financials()
                data['revenue'] = sales.revenue
                data['discs_count_sold'] = sales.discs_count_sold
            
            if 'delivery' in groups:
                delivery = await self.repo.get_in_transit_to_client_financial()
                data['on_way'] = delivery.on_way
                data['on_way_count'] = delivery.on_way_count
            
            if 'available' in groups:
                data['discs_count'] = await self.repo.count_available_discs()
            
            if 'assets' in groups:
                assets = await self.repo.get_assets_value()
                data['available_sum'] = assets.available_sum
                data['coming_to_me_sum'] = assets.coming_to_me_sum
            
            if 'avito' in groups:
                data['avito_expenses'] = await self.repo.get_expenses_by_transaction(
                    AVITO_TRANSACTION_TITLE
                )
            
            # Добавляем значения из .env
            data['initial_balance'] = self.config.INITIAL_BALANCE
            data['discs_count_sold'] = self.config.DISCS_COUNT_SOLD
            
            # Собираем отчёт (__post_init__ вычислит зависимые поля)
            report = FinanceReport(**data)
            
            logger.info(
                f"Finance report generated: groups={groups}, "
                f"incomes={report.incomes}, expenses={report.expenses}, "
                f"on_account={report.on_account}"
            )
            
            return report
            
        except Exception as e:
            logger.exception(f"Error generating finance report: {e}")
            raise