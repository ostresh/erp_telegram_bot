from aiogram.fsm.state import StatesGroup, State

class BuyGoodsSG(StatesGroup):
    type_game = State()
    receive_method = State()
    type_price_purchase = State()