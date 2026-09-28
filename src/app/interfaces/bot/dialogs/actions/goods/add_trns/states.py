from aiogram.fsm.state import State, StatesGroup

class AddTrnsSG(StatesGroup):
    util_select = State()
    input_price_purchase = State()
    input_comment = State()
    end_dialog = State()
    
    