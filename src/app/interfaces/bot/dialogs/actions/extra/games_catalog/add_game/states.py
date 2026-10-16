from aiogram.fsm.state import State, StatesGroup

class AddGameSG(StatesGroup):
    game_input = State()
    select_platform = State()