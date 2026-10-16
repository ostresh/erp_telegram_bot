from aiogram_dialog import Dialog

from app.interfaces.bot.dialogs.common import CommonWidgets
from app.interfaces.bot.dialogs.core import RootWindow

from .states import DeleteGameSG as States
from .event_handler import DeleteGameEventHandler as EventHandler

delete_game_dialog = Dialog(
    
    # первый этап - ввод названия игры
    RootWindow(
        *CommonWidgets.game_input(EventHandler),
        state=States.game_input,
    ),
)