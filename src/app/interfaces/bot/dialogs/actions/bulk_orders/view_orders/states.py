from aiogram.fsm.state import State, StatesGroup

class ViewOrdersSG(StatesGroup):
    select_bulk_order_id = State()
    
    
    