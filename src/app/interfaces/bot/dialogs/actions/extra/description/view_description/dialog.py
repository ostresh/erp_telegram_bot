from aiogram_dialog import Dialog

from app.interfaces.bot.dialogs.core import RootWindow

from .states import ViewDescriptionSG as States
from .event_handler import ViewDescriptionEventHandler as EventHandler


view_description_dialog = Dialog(
    
    #первый этап - получение описания
    RootWindow(
        state=States.get_description
    ),
    on_start=EventHandler.on_start
)