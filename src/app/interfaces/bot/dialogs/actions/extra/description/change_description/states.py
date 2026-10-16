from aiogram.fsm.state import State, StatesGroup

class ChangeDescriptionSG(StatesGroup):
    new_description_input = State()