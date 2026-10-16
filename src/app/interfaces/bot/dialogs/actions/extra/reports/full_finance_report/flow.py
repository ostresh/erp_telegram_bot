from aiogram_dialog import DialogManager

from app.core.db.unit_of_work import UnitOfWork
from app.core.service.reports.finance import FinanceService
from app.interfaces.bot.dialogs.common import CommonFlow
from app.interfaces.bot.utils.formatter import MessageFormatter


class FullFinanceReportFlow(CommonFlow):
    
    @classmethod
    async def get_full_finance_report(cls, manager: DialogManager) -> str:
        """
        Получение финансового отчета
        """
        
        uow: UnitOfWork = manager.middleware_data['uow']
        
        async with uow() as session:
            service = FinanceService(session)
            full_finance_report = await service.get_report()
            
        return MessageFormatter.format_finance_report(full_finance_report)