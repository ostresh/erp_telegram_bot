from aiogram.fsm.state import State, StatesGroup

class DeleteBulkOrderSG(StatesGroup):
    select_bulk_order_id = State()
    
    
    