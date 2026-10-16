from .reports import REPORTS_ROUTERS
from .games_catalog import GAMES_CATALOG_ROUTERS
from .description import DESCRIPTION_ROUTERS

EXTRA_ROUTERS = [
    *REPORTS_ROUTERS,
    *GAMES_CATALOG_ROUTERS,
    *DESCRIPTION_ROUTERS
]

__all__ = [
   'EXTRA_ROUTERS' 
]