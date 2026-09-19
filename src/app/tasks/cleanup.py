import asyncio
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="app.tasks.cleanup.cleanup_expired_messages",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def cleanup_expired_messages(self):
    """
    Периодическая задача для удаления устаревших сообщений.
    """
    logger.info("Starting cleanup_expired_messages task")
    
    try:
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(_run_cleanup())
            logger.info(f"Cleanup completed: {result}")
            return result
        finally:
            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                
                if pending:
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
            except Exception:
                pass
            
            loop.close()
    
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}", exc_info=True)
        raise self.retry(exc=e)


async def _run_cleanup() -> dict:
    """
    Асинхронная часть задачи очистки.
    
    Использует CeleryUnitOfWork с NullPool.
    """
    from app.db.unit_of_work import CeleryUnitOfWork
    from app.service import MessageCleanupService
    
    async with CeleryUnitOfWork() as session:
        service = MessageCleanupService(session)
        deleted = await service.cleanup_expired_messages()
        
        return {"messages_deleted": deleted}