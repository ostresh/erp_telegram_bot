from aiogram.fsm.state import State, StatesGroup

class ChangeRecordSG(StatesGroup):
    game_input = State()
    select_record_id = State()
    main = State()
    
    change_attribute = State()
    
    change_game = State()
    change_status = State()