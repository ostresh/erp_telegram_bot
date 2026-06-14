from aiogram import Router

from .base_commands_handler import router as base_router
from .bulk_orders_handlers import router as bulk_orders_router
from .games_handlers import router as games_router
from .info_handlers import router as info_router
from .inline_handlers import router as inline_router
from .notices_handlers import router as notices_router
from .records_handlers import router as records_router
from .menu_handlers import router as menu_router

# Создаем главный роутер
main_router = Router()

# Включаем все роутеры
main_router.include_routers(
    menu_router,
    base_router,
    records_router,
    notices_router,
    bulk_orders_router,
    games_router,
    info_router,
    inline_router,
    
)

# Экспортируем главный роутер
__all__ = ['main_router']
