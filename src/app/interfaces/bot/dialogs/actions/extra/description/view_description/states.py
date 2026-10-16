from aiogram.fsm.state import State, StatesGroup

class ViewDescriptionSG(StatesGroup):
    get_description = State()