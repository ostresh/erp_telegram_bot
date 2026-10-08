from aiogram_dialog import DialogManager

from app.core.db.unit_of_work import UnitOfWork
from app.core.service import MenuService
from app.core.service.menu.schemas import MenuConfig


class MenuMixin:
    """Получение меню (главное, предыдущее)."""

    @staticmethod
    async def get_main_menu(manager: DialogManager) -> MenuConfig:
        """
        Создаёт MenuConfig для главного меню.

        Используется при завершении диалогов
        для возврата пользователя в главное меню.

        Args:
            manager: DialogManager

        Returns:
            MenuConfig: конфигурация главного меню с текстом и клавиатурой
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            service = MenuService(session)
            main_menu = await service.get_menu('main')

        return main_menu

    @staticmethod
    async def get_back_menu(manager: DialogManager, path: str) -> MenuConfig:
        """
        Создаёт MenuConfig для предыдущего меню.

        Используется кнопкой "Назад" для возврата
        к меню, которое было до открытия диалога.

        Путь (например 'main-goods') определяет,
        какое родительское меню будет показано.

        Args:
            manager: DialogManager
            path: текущий путь меню (например, 'main-goods')

        Returns:
            MenuConfig: конфигурация предыдущего меню с текстом и клавиатурой
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            service = MenuService(session)
            back_menu = await service.get_back_menu(path)

        return back_menu