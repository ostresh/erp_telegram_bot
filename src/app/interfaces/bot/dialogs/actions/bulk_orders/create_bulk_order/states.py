from aiogram.fsm.state import State, StatesGroup

class CreateBulkOrderSG(StatesGroup):
    input_json = State()
    
    
    