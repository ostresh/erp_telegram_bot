import asyncio
import logging

from celery import shared_task
from aiogram.types import BufferedInputFile


from app.interfaces.bot.core.factory import create_bot
from app.interfaces.bot.utils.message import schedule_message_for_deletion
from app.core.service.labels import LabelService
from app.core.dto.labels import LabelDTO
from app.core.db.unit_of_work import CeleryUnitOfWork
from app.core.service.menu.service import MenuService

logger = logging.getLogger(__name__)

@shared_task(
    name='app.core.tasks.labels.generate_labels_pdf',
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def generate_labels_pdf(
    self,
    chat_id: int,
    message_id: int, 
    labels: list[dict]
):
    """
    Генерация этикеток
    
    Args:
        chat_id (int): id чата
        message_id (int): id сообщения
        labels (list[dict]): данные для DTO (Селери не может сериализировать данные из DTO, поэтому собираем прямо в таске)
    """
    
    logger.info(f"Start generating labels: {len(labels)}")
    
    dtos = [LabelDTO.model_validate(item) for item in labels]
    
    async def _run():
        
        async with CeleryUnitOfWork() as session:
            menu_service = MenuService(session)
            main_menu = await menu_service.get_menu('main')
        
        pdf_bytes = LabelService().generate(dtos)
        
        order_numbers = "_".join([item.order_number for item in dtos[0:2]])
        
        filename = (
            f"labels_"
            f"{order_numbers}.pdf"
        )
        
        async with create_bot() as bot:
            
            document = BufferedInputFile(
                pdf_bytes,
                filename=filename
            )
            
            caption = (
                f"🏷️ Сгенерированы этикетки для\n"
                f"{order_numbers}"
            )
            
            await schedule_message_for_deletion(
                await bot.send_document(
                    chat_id=chat_id,
                    document=document,
                    caption=caption
                ), CeleryUnitOfWork()
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
            
    try:
        asyncio.run(_run())

        logger.info(
            "Labels successfully sent to chat_id=%s",
            chat_id,
        )

        return {
            "status": "ok",
            "chat_id": chat_id,
            "message_id": message_id,
        }

    except Exception as exc:
        logger.exception("Failed to generate/send labels: %s", exc)
        
        try:
            
            asyncio.run(
                _send_error_message(
                    chat_id=chat_id,
                    message_id=message_id,
                    error_text="❌ Не получилось сформировать этикетки. Попробуй позже.",
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
    async with create_bot() as bot:
        await schedule_message_for_deletion(
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=error_text,
            ), CeleryUnitOfWork()
        )