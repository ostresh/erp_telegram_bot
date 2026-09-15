from dataclasses import dataclass, field
from typing import List, Union, Optional

from aiogram.types import InlineKeyboardMarkup



@dataclass
class MenuAction:
    """
    Действие, доступное в меню.
    
    Действие не ведёт в подменю,
    а запускает конкретную операцию (купить, продать и т.д.).
    
    Attributes:
        key: Короткий идентификатор действия (buy, sell, reserve)
        title: Отображаемое название с эмодзи
        handler_action: Значение для HandlerCB(action=...)
    """
    key: str
    title: str
    handler_action: str | None = None  # Если None, используется key


# Тип для одного дочернего элемента
ChildElement = Union['MenuNode', MenuAction]

# Тип для списка дочерних элементов (с поддержкой группировки через вложенные списки)
ChildrensList = List[Union[ChildElement, List[ChildElement]]]


@dataclass
class MenuNode:
    """
    Узел дерева меню.
    
    Содержит дочерние элементы (подменю и действия) в едином списке childrens.
    Порядок элементов в списке определяет порядок кнопок в клавиатуре.
    
    Группировка кнопок в ряды задаётся вложенными списками:
    - Одиночный элемент (например, `MenuAction(...)`) → 1 кнопка в ряд.
    - Список элементов (например, `[MenuAction(...), MenuAction(...)]`) → все кнопки в одном ряду.
    
    Пример:
        childrens=[
            [MenuAction1, MenuAction2],  # 2 кнопки в ряд
            MenuAction3,                  # 1 кнопка в ряд
            [MenuAction4, MenuAction5, MenuAction6],  # 3 кнопки в ряд
        ]
    
    Это создаст клавиатуру с рядами: [2, 1, 3]
    
    Attributes:
        key: Короткий идентификатор узла
        title: Отображаемое название
        childrens: Список дочерних элементов (с группировкой через вложенные списки)
        finance_fields: Поля финансового отчёта для этого меню
        
        path: Полный путь (заполняется автоматически)
        parent_path: Путь родителя (заполняется автоматически)
        crumbs: Хлебные крошки (заполняется автоматически)
    """
    key: str
    title: str
    childrens: ChildrensList = field(default_factory=list)
    finance_fields: List[str] = field(default_factory=list)
    
    # Заполняется автоматически:
    path: str = ''
    parent_path: Optional[str] = None
    crumbs: list[str] = field(default_factory=list)


@dataclass
class MenuConfig:
    """
    Конфигурация готового меню для отправки в Telegram
    
    Attributes:
        path: Полный путь
        keyboard: Inline клавиатура Telegram
        parent: Путь родителя
        text: Текст сообщения
    """
    path: str
    keyboard: InlineKeyboardMarkup
    parent: str | None = None
    text: str = ''