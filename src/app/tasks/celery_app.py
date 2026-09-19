from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_shutdown, worker_process_shutdown

from config import config

celery_app = Celery(
    'tasks',
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=['app.tasks.cleanup'],
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Europe/Moscow',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    worker_pool_restarts=True,
)

celery_app.conf.beat_schedule = {
    'cleanup-expired-messages': {
        'task': 'app.tasks.cleanup.cleanup_expired_messages',
        'schedule': crontab(minute=0)
    },
}

@worker_shutdown.connect
def on_worker_shutdown(**kwargs):
    """Закрывает бот и движки при остановке worker."""
    import asyncio
    from app.bot.core.celery_bot import close_bot
    from app.db.config import celery_engine
    
    loop = asyncio.new_event_loop()
    try:
        # Закрываем Bot
        loop.run_until_complete(close_bot())
        
        # Закрываем Celery движок
        loop.run_until_complete(celery_engine.dispose())
    finally:
        loop.close()


@worker_process_shutdown.connect
def on_worker_process_shutdown(**kwargs):
    """
    Вызывается при завершении дочернего процесса worker.
    
    Гарантирует что все ресурсы освобождены.
    """
    import asyncio
    from app.db.config import celery_engine
    
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(celery_engine.dispose())
        loop.close()
    except Exception:
        pass