from .goods_to_me import router as goods_to_me_router
from .goods_to_client import router as goods_to_client_router
from .available_records import router as available_records_router
from .available_games import router as available_games_router

WRH_DLVR = [
    goods_to_me_router,
    goods_to_client_router,
    available_records_router,
    available_games_router
]

__all__ = [
    'WRH_DLVR'
]