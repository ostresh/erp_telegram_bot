from aiogram_dialog import Dialog

from app.interfaces.bot.dialogs.core import RootWindow

from .states import FullFinanceReportSG as States
from .event_handler import FullFinanceReportEventHandler as EventHandler


full_finance_report_dialog = Dialog(
    
    RootWindow(
        state=States.get_full_finance_report
    ),
    on_start=EventHandler.on_start
)