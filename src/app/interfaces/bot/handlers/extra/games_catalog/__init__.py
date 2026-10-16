from .add_game import router as add_game_router
from .update_game import router as update_game_router
from .delete_game import router as delete_game_router

GAMES_CATALOG_ROUTERS = [
    add_game_router,
    update_game_router,
    delete_game_router
]

__all__ = [
    'GAMES_CATALOG_ROUTERS'
]