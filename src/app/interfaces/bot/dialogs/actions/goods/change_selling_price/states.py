from aiogram.fsm.state import State, StatesGroup

class ChangeSellingPriceSG(StatesGroup):
    game_input = State()
    input_price_selling = State()