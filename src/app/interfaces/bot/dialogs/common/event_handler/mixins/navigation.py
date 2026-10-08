from typing import TYPE_CHECKING, ClassVar

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from app.interfaces.bot.dialogs.core.decorators import handle_db_errors

if TYPE_CHECKING:
    from app.interfaces.bot.dialogs.common import CommonFlow


class NavigationMixin:
    """Обработчики навигации: кнопки "Назад" и "Закрыть"."""

    flow: ClassVar[type['CommonFlow']]
    
    @classmethod
    @handle_db_errors
    async def on_back(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Кнопка "Назад" в непервом окне диалога.

        Возвращает к предыдущему окну диалога
        Или переопределяется
        """
        await callback.answer()

        await manager.back(show_mode=ShowMode.EDIT)
    
    @classmethod
    @handle_db_errors
    async def on_back_menu(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Кнопка "Назад" в первом окне диалога.

        Возвращает к меню, которое было до открытия диалога.
        """
        await callback.answer()

        path = manager.start_data['path']
        menu = await cls.flow.get_back_menu(manager, path)
        
        await manager.done()
        await callback.message.edit_text(
            text=menu.text,
            reply_markup=menu.keyboard,
        )

    @classmethod
    @handle_db_errors
    async def on_close(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """Кнопка "Закрыть" — возврат в главное меню."""
        await callback.answer()

        main_menu = await cls.flow.get_main_menu(manager)

        await manager.done()
        await callback.message.edit_text(
            text=main_menu.text,
            reply_markup=main_menu.keyboard,
        )