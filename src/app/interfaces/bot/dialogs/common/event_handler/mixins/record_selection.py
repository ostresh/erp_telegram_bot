import logging
from typing import TYPE_CHECKING, ClassVar

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Select

from app.interfaces.bot.dialogs.core.decorators import handle_db_errors
from app.interfaces.bot.utils.emoji import Emoji

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.interfaces.bot.dialogs.common import CommonFlow

class RecordSelectionMixin:
    """Обработчики поиска игры и выбора записи."""

    flow: ClassVar[type['CommonFlow']]
    
    @classmethod
    @handle_db_errors
    async def on_game_typed(
        cls,
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: str,
    ):
        """
        Ввод названия игры.

        Проверяет существование игры, получает записи.
        При одной записи сразу автовыбирает её.
        """
        manager.show_mode = ShowMode.EDIT

        game_name = text.strip()
        manager.dialog_data['game_name'] = game_name
        manager.dialog_data['emoji_game'] = Emoji.GAME

        if not await cls.flow.is_game_exists(manager, game_name):
            await message.delete()
            return

        manager.dialog_data.pop('game_error', None)
        await message.delete()

        await cls._after_game_input(manager)

    @classmethod
    async def _after_game_input(cls, manager: DialogManager):
        """
        Дефолтная пост-обработка: получить записи,
        автовыбор при одной записи, переход к select_record_id.
        
        Переопределяется в диалогах с другой логикой.
        """
        records = await cls.flow.get_records(manager)

        if len(records) == 1:
            f_record = await cls.flow.format_record(manager, records[0].id)
            await cls.flow.set_record_in_dialog(manager, records[0].id, f_record)
            logger.info(
                f"One game '{manager.dialog_data['game_name']}' found, "
                f"switch to select_record_id",
            )

        logger.info(
            f"Game '{manager.dialog_data.get('game_name')}' found, "
            f"proceeding to next step",
        )
        await manager.switch_to(
            cls.states.select_record_id,
            show_mode=ShowMode.EDIT,
        )

    @classmethod
    @handle_db_errors
    async def on_record_id_selected(
        cls,
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: int,
    ):
        """Выбор ID записи — обновляет сообщение с форматированной записью."""
        await callback.answer()

        f_record = await cls.flow.format_record(manager, item_id)
        await cls.flow.set_record_in_dialog(manager, item_id, f_record)

    @classmethod
    async def on_select_record_id_button(
        cls,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """
        Кнопка "Далее" после выбора записи.

        Должна быть переопределена в каждом диалоговом обработчике.
        """
        raise NotImplementedError(
            f"{cls.__name__} must implement on_select_record_id_button"
        )