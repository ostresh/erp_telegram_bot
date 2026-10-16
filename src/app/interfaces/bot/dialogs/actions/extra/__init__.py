from .reports import REPORTS_DIALOGS
from .games_catalog import GAMES_CATALOG_DIALOGS
from .description import DESCRIPTION_DIALOGS

EXTRA_DIALOGS = [
    *REPORTS_DIALOGS,
    *GAMES_CATALOG_DIALOGS,
    *DESCRIPTION_DIALOGS
]

__all__ = [
    'EXTRA_DIALOGS'
]