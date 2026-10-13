from aiogram.fsm.state import State, StatesGroup

class BulkOrderArrivedSG(StatesGroup):
    select_bulk_order_id = State()
    
    