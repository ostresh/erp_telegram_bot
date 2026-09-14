from dataclasses import dataclass, field
from typing import List

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


@dataclass
class MenuNode:
    """
    Узел дерева меню.
    
    Содержит как дочерние меню (навигация),
    так и действия (операции на этом уровне).
    
    Attributes:
        key: Короткий идентификатор узла
        title: Отображаемое название
        children: Дочерние меню (MenuCB)
        actions: Действия на этом уровне (HandlerCB)
        with_finances: Добавлять ли финансы к тексту
        
        path: Полный путь (заполняется автоматически)
        parent_path: Путь родителя (заполняется автоматически)
        crumbs: Хлебные крошки (заполняется автоматически)
    """
    key: str
    title: str
    children: list['MenuNode'] = field(default_factory=list)
    actions: list['MenuAction'] = field(default_factory=list)
    finance_fields: List[str] = field(default_factory=list)
    
    # Заполняется автоматически:
    path: str = ''
    parent_path: str | None = None
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