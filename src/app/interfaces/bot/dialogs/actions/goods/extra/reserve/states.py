from aiogram.fsm.state import State, StatesGroup

class ReserveSG(StatesGroup):
    game_input = State()
    select_record_id = State()
    reserve_input = State()
    