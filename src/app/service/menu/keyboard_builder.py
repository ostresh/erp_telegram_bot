from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums.button_style import ButtonStyle

from app.service.menu.tree import MENU_INDEX
from app.bot.callbacks import MenuCB, ActionCB
from app.bot.messages.menu import MenuConstants
from .schemas import MenuAction, MenuNode, ChildElement

import logging

logger = logging.getLogger(__name__)


MENU_STYLE = ButtonStyle.DANGER
ACTION_STYLE = ButtonStyle.PRIMARY


class MenuKeyboardBuilder:
    """
    Генератор inline-клавиатур для меню.
    
    Автоматически создаёт клавиатуру на основе узла дерева меню.
    Порядок кнопок определяется порядком в дереве.
    """
    
    @staticmethod
    def build(path: str) -> InlineKeyboardBuilder:
        """
        Генерирует клавиатуру для указанного пути меню.
        
        Args:
            path: Путь меню (например, 'main' или 'main-info-records')
            row_width: Количество кнопок в ряду (по умолчанию 2)
            
        Returns:
            InlineKeyboardBuilder с готовой клавиатурой.
            Если путь не найден — возвращает пустой builder
            и логирует предупреждение.
        """
        
        builder = InlineKeyboardBuilder()
        node = MENU_INDEX.get(path)
        
        if not node:
            logger.warning(f"Unknown menu path: {path}")
            return builder
        
        row_pattern = []
        
        
        for child in node.childrens:
            if isinstance(child, list):
                for item in child:
                    MenuKeyboardBuilder._add_button(builder, item)
                row_pattern.append(len(child))
            else:
                MenuKeyboardBuilder._add_button(builder, child)
                row_pattern.append(1)
             
            
        if node.parent_path:
            builder.button(
                text=MenuConstants.BACK_TEXT,
                callback_data=MenuCB(path=node.path, title='back').pack()
            )
            
        if row_pattern:
            builder.adjust(*row_pattern)
        
        return builder.as_markup()
    
    @staticmethod
    def _add_button(builder: InlineKeyboardBuilder, item: ChildElement) -> None:
        """
        Добавляет кнопку в builder в зависимости от типа элемента.
        
        Args:
            builder: InlineKeyboardBuilder
            item: MenuNode или MenuAction
        """
        
        if isinstance(item, MenuAction):
            handler_action = item.handler_action or item.key
            builder.button(
                text = item.title,
                callback_data=ActionCB(path=item.path, action=handler_action).pack(),
                style=ACTION_STYLE
            )
        elif isinstance(item, MenuNode):
            builder.button(
                text = f'{item.title}',
                callback_data=MenuCB(path=item.path, title=item.key).pack(),
                style=MENU_STYLE
            )