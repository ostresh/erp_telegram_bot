# main.py (в корне проекта)
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import config
from database import db
from bot.handlers import main_router
from bot.middleware.auth_middlewares import AuthMiddleware

async def main():
    """Основная функция запуска бота"""
    
    # Проверяем наличие токена
    if not config.BOT_TOKEN:
        print("Добавь BOT_TOKEN в файл .env")
        return
    
    # Инициализация бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        # Подключаемся к базе данных
        await db.connect()
        
        dp.message.middleware(AuthMiddleware())
        if hasattr(dp.callback_query, 'middleware'):
            dp.callback_query.middleware(AuthMiddleware())
        
        dp.include_router(main_router)
        
        db_status = await db.test_connection()
        print(db_status)
        
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(f'Ошибка: {e}')
    finally:
        await db.close()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")