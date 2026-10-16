from aiogram.fsm.state import State, StatesGroup

class ProductReportSG(StatesGroup):
    type_period = State()
    
    
    