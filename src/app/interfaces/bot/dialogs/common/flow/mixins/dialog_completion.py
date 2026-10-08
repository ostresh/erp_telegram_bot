from typing import List, Union

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager

from app.core.db.unit_of_work import UnitOfWork
from app.core.service.menu.schemas import MenuConfig
from app.core.utils import schedule_message_for_deletion


class DialogCompletionMixin:
    """Завершение диалога с отправкой результата пользователю."""

    @classmethod
    async def finish_dialog_with_result(
        cls,
        manager: DialogManager,
        text: str,
    ) -> None:
        """
        Завершает диалог и отправляет один результат пользователю.

        Поведение:
            - Сообщение результата помечается на автоудаление
            - Главное меню отправляется в чат отдельным сообщением
            - Диалог закрывается через manager.done()

        Для CallbackQuery:
            редактирует текущее сообщение под результат

        Для Message:
            удаляет сообщение пользователя и редактирует последнее сообщение диалога

        Побочные эффекты:
            - Планирует удаление сообщения результата через schedule_message_for_deletion
            - Отправляет главное меню
            - Закрывает диалог

        Args:
            manager: DialogManager
            text: текст результата для показа пользователю
        """
        uow: UnitOfWork = manager.middleware_data["uow"]
        main_menu: MenuConfig = await cls.get_main_menu(manager)
        event: Union[Message, CallbackQuery] = manager.event

        if isinstance(event, CallbackQuery):
            await event.answer()

            await schedule_message_for_deletion(
                await event.message.edit_text(text=text),
                uow,
            )
            await event.message.answer(
                text=main_menu.text,
                reply_markup=main_menu.keyboard,
            )

        elif isinstance(event, Message):
            await event.delete()

            last_message_id = manager.current_stack().last_message_id
            await schedule_message_for_deletion(
                await event.bot.edit_message_text(
                    text=text,
                    message_id=last_message_id,
                    chat_id=event.chat.id,
                ),
                uow,
            )
            await event.answer(
                text=main_menu.text,
                reply_markup=main_menu.keyboard,
            )

        await manager.done()

    @classmethod
    async def finish_dialog_with_many_result(
        cls,
        manager: DialogManager,
        texts: List[str],
    ) -> None:
        """
        Завершает диалог и отправляет несколько результатов пользователю.

        Используется, когда результат — список записей
        (например, при обмене или массовом обновлении).

        Поведение:
            - Каждое сообщение результата помечается на автоудаление
            - Главное меню отправляется в конце отдельным сообщением
            - Диалог закрывается через manager.done()

        Для CallbackQuery:
            отправляет каждый результат отдельным сообщением

        Для Message:
            удаляет сообщение пользователя, отправляет результаты как ответы

        Побочные эффекты:
            - Планирует удаление каждого сообщения результата
            - Отправляет главное меню
            - Закрывает диалог

        Args:
            manager: DialogManager
            texts: список текстов результатов для показа пользователю
        """
        uow: UnitOfWork = manager.middleware_data["uow"]
        main_menu: MenuConfig = await cls.get_main_menu(manager)
        event: Union[Message, CallbackQuery] = manager.event

        if isinstance(event, CallbackQuery):
            await event.answer()

            for text in texts:
                await schedule_message_for_deletion(
                    await event.message.answer(text=text),
                    uow,
                )
            await event.message.answer(
                text=main_menu.text,
                reply_markup=main_menu.keyboard,
            )

        elif isinstance(event, Message):
            await event.delete()

            for text in texts:
                await schedule_message_for_deletion(
                    await event.answer(text=text),
                    uow,
                )
            await event.answer(
                text=main_menu.text,
                reply_markup=main_menu.keyboard,
            )

        await manager.done()