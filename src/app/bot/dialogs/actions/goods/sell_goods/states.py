from aiogram.fsm.state import StatesGroup, State

class SellGoodsSG(StatesGroup):
    type_game = State()
    select_record_id = State()
    receive_method = State()
    type_price_sold = State()
    