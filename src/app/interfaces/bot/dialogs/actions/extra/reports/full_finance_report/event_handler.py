from typing import Any, ClassVar

from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors

from .states import FullFinanceReportSG
from .flow import FullFinanceReportFlow

class FullFinanceReportEventHandler(CommonEventHandler):
    """
    Обработчик для full_finance_report
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: FullFinanceReportFlow
        - States: FullFinanceReportSG
    """
    flow: ClassVar[type[FullFinanceReportFlow]] = FullFinanceReportFlow
    states: ClassVar[type[FullFinanceReportSG]] = FullFinanceReportSG
    
    @classmethod
    @handle_db_errors
    async def on_start(cls, start_data: Any, manager: DialogManager):
        """Выгрузка финансового отчета"""
        
        full_finance_report = await cls.flow.get_full_finance_report(manager)
        
        await cls.flow.finish_dialog_with_result(manager, full_finance_report)
        
        
        
        