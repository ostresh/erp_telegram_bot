import asyncio
import logging
from aiogram import Dispatcher
from aiogram_dialog import setup_dialogs

from config import config
from app.interfaces.bot.core.factory import create_bot
from app.core.db.config import AsyncSessionLocal, close_db
from app.core.db.unit_of_work import UnitOfWork
from app.interfaces.bot.handlers import main_router
from app.interfaces.bot.middlewares import AuthMiddleware, UnitOfWorkMiddleware
from app.interfaces.bot.dialogs import register_dialogs
from app.core.utils.logger import setup_logger

# Настройка логирования
setup_logger()
logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    
    # Проверяем наличие токена
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN is not set in .env file")
        return
    
    bot = create_bot()
    
    dp = Dispatcher()
    
    # Создаём UnitOfWork
    uow = UnitOfWork(session_factory=AsyncSessionLocal)
    
    try:
        # Регистрируем middleware
        dp.update.outer_middleware(UnitOfWorkMiddleware(uow))
        dp.message.middleware(AuthMiddleware())
        dp.callback_query.middleware(AuthMiddleware())
        
        # Подключаем роутеры
        dp.include_router(main_router)
        
        # ПОТОМ диалоги
        register_dialogs(dp)

        # В КОНЦЕ setup_dialogs — обязательно последним!
        setup_dialogs(dp)
        
        # Тест подключения к БД
        async with uow() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        # Запуск бота
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("🚀 Bot started")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.exception(f"Critical error: {e}")
        
    finally:
        await bot.session.close()
        await close_db()
        logger.info("👋 Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")