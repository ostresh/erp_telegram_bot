from aiogram.filters.callback_data import CallbackData

class MenuCB(CallbackData, prefix = 'menu'):
    path: str
    title: str
    
class HandlerCB(CallbackData, prefix = 'handler'):
    action: str
    
