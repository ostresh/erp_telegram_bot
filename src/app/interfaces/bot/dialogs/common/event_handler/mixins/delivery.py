import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select

from app.interfaces.bot.dialogs.common.mapping import DeliveryMapping

logger = logging.getLogger(__name__)


class DeliveryMixin:
    """Обработчики для диалогов с выбором метода доставки (локально/доставка)."""

    @staticmethod
    async def on_receive_method_selected(
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str,
    ):
        """Выбор метода получения товара."""
        await callback.answer()

        manager.dialog_data['receive_type'] = item_id
        manager.dialog_data['receive_title'] = DeliveryMapping.TITLES[item_id]

        logger.info(f"Receive method {item_id}, proceeding to next step")
        await manager.next(show_mode=ShowMode.EDIT)