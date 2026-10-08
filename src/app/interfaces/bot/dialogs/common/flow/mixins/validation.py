from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from app.core.db.unit_of_work import UnitOfWork
from app.core.service import GameService


class GameValidationMixin:
    """Проверки валидности данных для диалогов."""

    @staticmethod
    async def is_game_exists(manager: DialogManager, game_name: str) -> bool:
        """
        Проверка, существует ли игра в списке.

        Если не существует:
            записывает ошибку в dialog_data['game_error'],
            чтобы окно показало её пользователю.

        Побочный эффект:
            При неудаче устанавливает manager.dialog_data['game_error']

        Args:
            manager: DialogManager
            game_name: название игры

        Returns:
            bool: существует ли игра
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            game_service = GameService(session)
            is_exists = await game_service.is_game_exists(game_name)

        if not is_exists:
            manager.dialog_data['game_error'] = (
                f'Игра "{game_name}" не найдена. Попробуйте ещё раз'
            )
            return False

        return True

    @staticmethod
    async def is_record_id_selected(
        callback: CallbackQuery,
        manager: DialogManager,
    ) -> bool:
        """
        Проверяет, выбран ли record_id.

        Если не выбран:
            выводит предупреждение пользователю через alert.

        Побочный эффект:
            При неудаче отвечает на callback с show_alert=True

        Args:
            callback: CallbackQuery для ответа пользователю
            manager: DialogManager

        Returns:
            bool: выбран ли record_id
        """
        if manager.dialog_data.get('record_id') is None:
            await callback.answer(
                "⚠️ Сначала выберите ID записи!",
                show_alert=True,
            )
            return False

        return True