from aiogram.fsm.state import State, StatesGroup

class DeleteRecordSG(StatesGroup):
    record_input = State()