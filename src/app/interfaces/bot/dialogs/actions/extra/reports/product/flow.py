from aiogram_dialog import DialogManager

from app.interfaces.bot.dialogs.common import CommonFlow
from app.core.tasks.report.movement import generate_movement_report_excel_task
from app.core.tasks.report.sales import generate_sales_report_excel_task
import logging

logger = logging.getLogger(__name__)

class ProductReportFlow(CommonFlow):
    
    @staticmethod
    async def start_report_generation (
        manager: DialogManager, 
        chat_id: int,
        message_id: int,
        period_start_str: str,
        period_end_str: str) -> None:
        """
        Получение отчета
        """
        
        action_type = manager.start_data.get('handler_action')
        
        if action_type == 'movement_report':
            generate_movement_report_excel_task.delay(
                chat_id=chat_id,
                message_id=message_id,
                period_start_str=period_start_str,
                period_end_str=period_end_str
            )
        elif action_type == 'sales_report':
            generate_sales_report_excel_task.delay(
                chat_id=chat_id,
                message_id=message_id,
                period_start_str=period_start_str,
                period_end_str=period_end_str  
            )
        else:
            logger.exception(f'Incorrect action_type')
            raise ValueError()
        
        
        