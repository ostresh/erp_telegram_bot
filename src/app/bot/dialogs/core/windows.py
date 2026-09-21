from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Group
from typing import Optional

from app.bot.dialogs.common.navigation import CommonDialogNavigation


class BaseWindow(Window):
    """
    Базовый класс для кастомного окна
    
    Позволяет автоматически добавить
    В конец кнопки "Назад" и "Закрыть"
    
    Args:
        is_root: Первое ли окно в диалоге
    """
    
    
    def __init__(
        self,
        *widgets,
        is_root: bool = True,
        **kwargs
    ):
       
       nav = (
           CommonDialogNavigation.root_controls
           if is_root
           else CommonDialogNavigation.inner_controls
       )
       
       super().__init__(*widgets, nav, **kwargs)
       
class RootWindow(BaseWindow):
    """
    Кастомный класс для первого окна в диалоге
    
    Позволяет автоматически добавить
    В конец кнопки "Назад" и "Закрыть"
    
    *кнопка "Назад" перенаправляет в меню до нажатия кнопки действия
    *кнопка "Закрыть" перенаправляет в главное меню
    """
    
    def __init__(self, *widgets, **kwargs):
        super().__init__(*widgets, is_root=True, **kwargs)
        
class InnerWindow(BaseWindow):
    """
    Кастомный класс для непервого окна в диалоге
    
    Позволяет автоматически добавить
    В конец кнопки "Назад" и "Закрыть"
    
    *кнопка "Назад" перенаправляет в предыдущее меню активного диалога
    *кнопка "Закрыть" перенаправляет в главное меню
    """
    
    def __init__(self, *widgets, **kwargs):
        super().__init__(*widgets, is_root=False, **kwargs) 