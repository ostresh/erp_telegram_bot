from aiogram.fsm.state import State, StatesGroup

class DeleteGameSG(StatesGroup):
    game_input = State()