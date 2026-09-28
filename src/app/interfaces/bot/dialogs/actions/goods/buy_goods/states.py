from aiogram.fsm.state import State, StatesGroup

class BuyGoodsSG(StatesGroup):
    game_input = State()
    receive_method = State()
    input_price_purchase = State()