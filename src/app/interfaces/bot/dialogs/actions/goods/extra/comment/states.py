from aiogram.fsm.state import State, StatesGroup

class CommentSG(StatesGroup):
    game_input = State()
    select_record_id = State()
    comment_input = State()
    