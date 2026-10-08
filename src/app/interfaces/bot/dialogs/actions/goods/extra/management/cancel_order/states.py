from aiogram.fsm.state import State, StatesGroup

class CancelOrderSG(StatesGroup):
    game_input = State()
    select_record_id = State()
    