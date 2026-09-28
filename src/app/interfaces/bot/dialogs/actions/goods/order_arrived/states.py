from aiogram.fsm.state import State, StatesGroup

class OrderArrivedSG(StatesGroup):
    game_input = State()
    select_record_id = State()
    select_order_recipient = State()
    