from aiogram.filters.callback_data import CallbackData
    
class ActionCB(CallbackData, prefix = 'action'):
    path: str
    action: str
    
