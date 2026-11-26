from aiogram.fsm.state import State, StatesGroup

class CreateLabelsSG(StatesGroup):
    # основное окно
    main = State()
    
    # окна добавления заказа
    # введение номера
    order_number_input = State()
    # выбор доставки
    delivery_input = State()
    # добавление игр
    # главное окно добавления игр
    main_game_input = State()
    # добавление игр
    game_input = State() 
    
    