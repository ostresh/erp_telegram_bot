import asyncio
from datetime import datetime, timezone
import logging

from celery import shared_task
from aiogram.types import BufferedInputFile

from app.core.db.unit_of_work import CeleryUnitOfWork
from app.core.service.reports.sales import SalesService
from app.interfaces.bot.core.celery_bot import get_bot
from app.interfaces.bot.utils.message import schedule_message_for_deletion
from app.core.service.menu.service import MenuService

logger = logging.getLogger(__name__)

DATE_FORMAT = '%d.%m.%Y'

@shared_task(
    name="app.core.tasks.report.movement.generate_movement_report_excel",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def generate_movement_report_excel_task(
    self,
    chat_id: int,
    message_id: int,
    period_start_str: str,
    period_end_str: str
):
    """
    Генерация отчета по движению товаров за период
    
    Args:
        chat_id (int): id чата
        message_id (int): id сообщения
        period_start_str (str): начало периода в виде строки
        period_end_str (str): конец периода в виде строки
    """
    
    period_start = datetime.strptime(period_start_str, DATE_FORMAT).replace(tzinfo=timezone.ufc)
    period_end = datetime.strptime(period_end_str, DATE_FORMAT).replace(tzinfo=timezone.ufc)
    
    logger.info(
        "Start generating sales report for chat_id=%s, message_id=%s, period=[%s, %s]",
        chat_id,
        message_id,
        period_start,
        period_end,
    )
    
    async def _run():
        
        async with CeleryUnitOfWork() as session:
            sales_service = SalesService(session)
            menu_service = MenuService(session)
            
            excel_bytes = await sales_service.export_movement_report_to_excel(period_start, period_end)
            main_menu = await menu_service.get_menu('main')
          
        filename = (
            f"movement_report_"
            f"{period_start:%Y-%m-%d}_"
            f"{period_end:%Y-%m-%d}.xlsx"
        )
        
        bot = get_bot()
        
        try:
            
            document = BufferedInputFile(
                excel_bytes,
                filename=filename
            )
            
            caption = (
                f"📊 Отчёт по движению товаров\n"
                f"Период: {period_start:%d.%m.%Y} — {period_end:%d.%m.%Y}"
            )
            
            await schedule_message_for_deletion(
                        await bot.send_document(
                        chat_id=chat_id,
                        document=document,
                        caption=caption
                ), CeleryUnitOfWork
            )
            
            await bot.send_message(
                chat_id=chat_id,
                text=main_menu.text,
                reply_markup=main_menu.keyboard,
            )
            
            await bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )
        
        finally:
            await bot.session.close()
            
    try:
        asyncio.run(_run())

        logger.info(
            "Sales report successfully sent to chat_id=%s",
            chat_id,
        )

        return {
            "status": "ok",
            "chat_id": chat_id,
            "message_id": message_id,
        }

    except Exception as exc:
        logger.exception("Failed to generate/send sales report: %s", exc)

        try:
            
            asyncio.run(
                _send_error_message(
                    chat_id=chat_id,
                    message_id=message_id,
                    error_text="❌ Не получилось сформировать отчёт. Попробуй позже.",
                )
            )
        except Exception:
            logger.exception("Failed to send error message to Telegram")

        raise self.retry(exc=exc)
    
async def _send_error_message(
    chat_id: int,
    message_id: int,
    error_text: str, 
) -> None:
    bot = get_bot()

    try:
        await schedule_message_for_deletion(
           await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=error_text,
            ), CeleryUnitOfWork
        )
        
    finally:
        await bot.session.close()