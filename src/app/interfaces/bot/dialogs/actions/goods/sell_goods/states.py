from aiogram.fsm.state import State, StatesGroup

class SellGoodsSG(StatesGroup):
    game_input = State()
    select_record_id = State()
    receive_method = State()
    input_price_sold = State()
    