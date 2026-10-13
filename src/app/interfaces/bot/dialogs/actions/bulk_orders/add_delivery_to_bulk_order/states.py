from aiogram.fsm.state import State, StatesGroup

class AddDeliveryToBulkOrderSG(StatesGroup):
    select_bulk_order_id = State()
    input_delivery_price = State()
    
    