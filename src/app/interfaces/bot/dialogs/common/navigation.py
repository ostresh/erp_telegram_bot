from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.text import Const

from app.interfaces.bot.messages.menu import MenuConstants
from .event_handler import CommonEventHandler


class CommonDialogNavigation:
    """
    Общие элементы навигации для диалогов.

    Содержит готовые кнопки и строки для навигации:
    - Возврат в меню (для первого окна)
    - Возврат по диалогу (для внутренних окон)
    """
    
    @staticmethod
    def root_controls(back_button: Button | None = None) -> Row[Button, Button]:
        """
        Кнопки управления первым окном
        Если задан back_button, то ставится кастомная кнопка
        
        Args:
            back_button: Button кастомная
            
        Returns:
            Row с кнопкой "Назад" и "Закрыть"
        """
        return Row(
            back_button or Button(
                Const(MenuConstants.BACK_TEXT),
                id='back_menu_button',
                on_click=CommonEventHandler.on_back_menu,
            ),
            Button(
                Const(MenuConstants.CLOSE_TEXT),
                id='close_button',
                on_click=CommonEventHandler.on_close,
            ),
        )
    
    @staticmethod
    def inner_controls(back_button: Button | None = None) -> Row[Button, Button]:
        """
        Кнопки управления первым окном
        Если задан back_button, то ставится кастомная кнопка
        
        Args:
            back_button: Button кастомная
            
        Returns:
            Row с кнопкой "Назад" и "Закрыть"
        """
        return Row(
            back_button or Button(
                Const(MenuConstants.BACK_TEXT),
                id='back_menu_button',
                on_click=CommonEventHandler.on_back,
            ),
            Button(
                Const(MenuConstants.CLOSE_TEXT),
                id='close_button',
                on_click=CommonEventHandler.on_close,
            ),
        )
