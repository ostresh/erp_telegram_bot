from .reports import REPORTS_ROUTERS
from .games_catalog import GAMES_CATALOG_ROUTERS

EXTRA_ROUTERS = [
    *REPORTS_ROUTERS,
    *GAMES_CATALOG_ROUTERS
]

__all__ = [
   'EXTRA_ROUTERS' 
]