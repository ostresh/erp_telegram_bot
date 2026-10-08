from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput, TextInput


class ValidationMixin:
    """Обработчики ошибок ввода и неожиданных сообщений."""

    @staticmethod
    async def on_int_error(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        error: ValueError,
    ):
        """Ошибка ввода целого числа (цена, ID)."""
        await message.answer("❌ Введите целое число!")

    @staticmethod
    async def on_text_error(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        error: ValueError,
    ):
        """Ошибка ввода строки."""
        await message.answer("❌ Введите правильную строку!")

    @staticmethod
    async def on_unexpected_message(
        message: Message,
        widget: MessageInput,
        manager: DialogManager,
    ):
        """Сообщение, отправленное мимо кнопок — удаляется."""
        manager.show_mode = ShowMode.EDIT
        await message.delete()