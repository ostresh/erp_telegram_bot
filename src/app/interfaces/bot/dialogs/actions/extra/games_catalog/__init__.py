from .add_game.dialog import add_game_dialog
from .update_game.dialog import update_game_dialog
from .delete_game.dialog import delete_game_dialog

GAMES_CATALOG_DIALOGS = [
    add_game_dialog,
    update_game_dialog,
    delete_game_dialog
]

__all__ = [
    'GAMES_CATALOG_DIALOGS'
]