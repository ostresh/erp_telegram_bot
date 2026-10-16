from aiogram.fsm.state import State, StatesGroup

class UpdateGameSG(StatesGroup):
    game_input = State()
    new_name_input = State()