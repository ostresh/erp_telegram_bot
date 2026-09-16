from aiogram import Router

from .start import router as start_router
from .navigation import router as navigation_router


main_router = Router(name="main")

main_router.include_routers(
    start_router,
    navigation_router,
)

__all__ = ["main_router"]