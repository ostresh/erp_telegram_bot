from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram.fsm.state import State
from aiogram_dialog import Window

from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.window import UNSET_PARSE_MODE, _DEFAULT_MARKUP_FACTORY
from aiogram_dialog.widgets.input import MessageInput

if TYPE_CHECKING:
    from aiogram_dialog.widgets.kbd import Keyboard
    from aiogram_dialog.window import (
        GetterVariant,
        MarkupFactory,
        OnResultEvent,
        WidgetSrc,
    )


class BaseWindow(Window):
    """
    Базовый класс для кастомного окна

    Позволяет автоматически добавить
    в конец кнопки "Назад" и "Закрыть"

    Тип навигации задаётся класс-атрибутом is_root
    в подклассах RootWindow / InnerWindow
    
    Проверяет, есть ли виджет ввода
    Если нет, добавит виджет ввода и обработчик, который
    удалит сообщение пользователя (если нет виджета ввода, то
    диалог ждет нажатия на кнопку, а не ввода сообщения)
    """

    is_root: bool = True

    def __init__(
        self,
        *widgets: WidgetSrc,
        state: State,
        getter: GetterVariant = None,
        on_process_result: OnResultEvent | None = None,
        markup_factory: MarkupFactory = _DEFAULT_MARKUP_FACTORY,
        parse_mode: str | None = UNSET_PARSE_MODE,
        disable_web_page_preview: bool | None = None,
        protect_content: bool | None = None,
        preview_add_transitions: list[Keyboard] | None = None,
        preview_data: GetterVariant = None,
        back_button: Button | None = None,
        **kwargs: Any,
    ) -> None:
        from app.interfaces.bot.dialogs.common.navigation import CommonDialogNavigation

        nav = (
            CommonDialogNavigation.root_controls(back_button)
            if self.is_root
            else CommonDialogNavigation.inner_controls(back_button)
        )

        final_widgets = list(widgets)
        
        if not self._has_input_widget(widgets):
            from app.interfaces.bot.dialogs.common.event_handler.mixins import ValidationMixin
            final_widgets.append(
                MessageInput(ValidationMixin.on_unexpected_message)
            )
        
        super().__init__(
            *final_widgets,
            nav,
            state=state,
            getter=getter,
            on_process_result=on_process_result,
            markup_factory=markup_factory,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            protect_content=protect_content,
            preview_add_transitions=preview_add_transitions,
            preview_data=preview_data,
            **kwargs,
        )
        
    @staticmethod
    def _has_input_widget(widgets: WidgetSrc) -> bool:
        """
        Проверяет, есть ли виджет ввода у окна
        """
        return any(isinstance(widget, MessageInput) for widget in widgets)
        


class RootWindow(BaseWindow):
    """
    Кастомный класс для первого окна в диалоге

    Позволяет автоматически добавить
    в конец кнопки "Назад" и "Закрыть"

    *кнопка "Назад" перенаправляет в меню до нажатия кнопки действия
    *кнопка "Закрыть" перенаправляет в главное меню
    """

    is_root = True


class InnerWindow(BaseWindow):
    """
    Кастомный класс для непервого окна в диалоге

    Позволяет автоматически добавить
    в конец кнопки "Назад" и "Закрыть"

    *кнопка "Назад" перенаправляет в предыдущее меню активного диалога
    *кнопка "Закрыть" перенаправляет в главное меню
    """

    is_root = False