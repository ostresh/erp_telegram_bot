from typing import ClassVar

from aiogram.fsm.state import StatesGroup

from .mixins import (
    DeliveryMixin,
    NavigationMixin,
    RecordSelectionMixin,
    ValidationMixin
)
from app.interfaces.bot.dialogs.common.flow import CommonFlow


class CommonEventHandler(
    DeliveryMixin,
    NavigationMixin,
    RecordSelectionMixin,
    ValidationMixin
):
    """
    Базовый обработчик всех диалогов.

    Содержит только конфигурацию (flow, states).
    Поведение собирается из миксинов при наследовании.
    """

    flow: ClassVar[type[CommonFlow]] = CommonFlow
    states: ClassVar[type[StatesGroup]] = None