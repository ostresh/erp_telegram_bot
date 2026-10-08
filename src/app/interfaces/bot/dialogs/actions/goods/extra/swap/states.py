from aiogram.fsm.state import State, StatesGroup

class SwapSG(StatesGroup):
    main = State()
    giving_input = State()
    getting_input = State()
    select_record_id = State()