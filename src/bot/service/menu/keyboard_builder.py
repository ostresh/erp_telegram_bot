from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.service.menu.tree import MENU_INDEX
from bot.app.callbacks.callbacks import MenuCB, HandlerCB
from bot.app.messages.menu import MenuConstants
import logging

logger = logging.getLogger(__name__)


class KeyboardBuilder:
    """
    Генератор inline-клавиатур для меню.
    
    Автоматически создаёт клавиатуру на основе узла дерева меню.
    Порядок кнопок:
    1. Действия (HandlerCB) — операции на текущем уровне
    2. Дочерние меню (MenuCB) — навигация в подменю
    3. Кнопка "Назад" — возврат к родителю (если есть)
    """
    
    @staticmethod
    def build(path: str, row_width: int = 1) -> InlineKeyboardBuilder:
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
        
        for action in node.actions:
            handler_action = action.handler_action or action.key
            builder.button(
                title = action.title,
                callback_data=HandlerCB(action=handler_action).pack()
            )
            
        for child in node.children:
            builder.button(
                text=child.title,
                callback_data=MenuCB(path=child.path, title=child.key).pack()
            )
            
        if node.parent_path:
            builder.button(
                text=MenuConstants.BACK_TEXT,
                callback_data=MenuCB(path=node.parent_path, title='back').pack()
            )
            
        builder.adjust(row_width)
        
        return builder