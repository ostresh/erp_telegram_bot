from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from bot.service.menu.schemas import MenuConfig
from bot.service.menu.tree import MENU_INDEX
from bot.service.menu.keyboard_builder import MenuKeyboardBuilder
from bot.app.messages.menu import MenuConstants
from bot.utils.formatter import MessageFormatter
from bot.service.finance import FinanceService
import logging

logger = logging.getLogger(__name__)


class MenuService:
    """
    Сервис для создания меню бота.
    
    Генерирует готовые данные меню (текст + клавиатура)
    по пути навигации. Для главного меню добавляет
    финансовую информацию из БД.
    
    Usage:
        menu_service = MenuService(session)
        menu = await menu_service.get_menu('main-info')
        await message.answer(text=menu.text, reply_markup=menu.keyboard)
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            session: Активная сессия БД из UnitOfWork
        """
        self.session = session
        
    def _build_breadcrumbs_text(self, crumbs: List[str]) -> str:
        """
        Собирает текст хлебных крошек из списка заголовков.
        
        Первый заголовок выводится без стрелки,
        остальные — со стрелкой '→'.
        
        Args:
            crumbs: Список заголовков, например ['Главная', 'Информация', 'Записи']
            
        Returns:
            HTML-текст с хлебными крошками
            
        Example:
            ['Главная', 'Информация'] → '<b>Главная</b>\\n→<b>Информация</b>'
        """
        
        parts = []
        
        for i, title in enumerate(crumbs):
            if i == 0:
                parts.append(f'<b>{title}</b>')
            else:
                parts.append(f'→<b>{title}</b>')
        
        return '\n'.join(parts)
    
    async def _get_finances(self, fields: List) -> str:
        """
        Получает финансовую информацию.
        
        Возвращает отформатированный текст с показателями.
        При ошибке возвращает пустую строку,
        чтобы меню всё равно отобразилось.
        
        Returns:
            Отформатированный текст финансов или пустая строка
        """
        
        try:
            service = FinanceService(self.session)
            report = await service.get_report(fields)
            return MessageFormatter.format_finance_report(
                report,
                fields
            )
        except Exception as e:
            logger.exception(f"Error getting finances for main menu: {e}")
            return ''
        
    async def get_menu(self, path: str) -> MenuConfig:
        """
        Создаёт меню по пути навигации.
        
        Генерирует клавиатуру и текст хлебных крошек
        
        Args:
            path: Путь меню (например, 'main' или 'main-info-records')
            
        Returns:
            MenuConfig с текстом, клавиатурой и метаданными
            
        Raises:
            ValueError: Если путь не найден в дереве меню
        """
        
        logger.debug(f"Building menu for path: {path}")
    
        node = MENU_INDEX.get(path)
        if not node:
            logger.warning(f"Unknown menu path: {path}")
            raise ValueError(f"Unknown menu path: {path}")
        
        # Генерируем клавиатуру
        keyboard = MenuKeyboardBuilder.build(node.path)
        
        # Генерируем текст хлебных крошек
        text = self._build_breadcrumbs_text(node.crumbs)
        
        # Если у узла указаны финансовые поля — добавляем финансовую информацию
        if node.finance_fields:
            finance_text = await self._get_finances(node.finance_fields)
            if finance_text:
                text = finance_text + '\n\n' + text
        
        # Добавляем стандартное окончание
        text = text + '\n\n' + MenuConstants.ADDON_TEXT
        
        return MenuConfig(
            path=node.path,
            keyboard=keyboard,
            parent=node.parent_path,
            text=text,
        )
        
    async def get_back_menu(self, path: str) -> MenuConfig:
        """
        Создаёт меню для возврата (родительское меню).
        
        Если у текущего меню нет родителя, возвращает главное меню.
        
        Args:
            path: Текущий путь меню
            
        Returns:
            MenuConfig родительского меню (или главного, если родителя нет)
        """
        logger.debug(f"Building back menu for path: {path}")
        
        node = MENU_INDEX.get(path)
        
        if not node or not node.parent_path:
            return await self.get_menu('main')
        
        return await self.get_menu(node.parent_path)