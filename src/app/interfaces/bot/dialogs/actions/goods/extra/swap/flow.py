from datetime import datetime, timezone
from typing import Any

from aiogram_dialog import DialogManager

from app.core.db.statuses.record import RecordStatus
from app.interfaces.bot.dialogs.common import CommonFlow

import logging

logger = logging.getLogger(__name__)

class SwapFlow(CommonFlow):
    
    @classmethod
    async def get_records(cls, manager: DialogManager):
        """
        Переопределение стандартного метода
        Получаем записи определенной игры и определенного получателя
        """
        game_name = manager.dialog_data.get('game_name')
        return await cls.get_available_records_by_game(manager, game_name)
    
    @classmethod
    def add_game_out(cls, manager: DialogManager) -> None:
        """
        Добавляет выбранную запись в исходящие
        
        - отформатированная запись → games_out (для вывода)
        - id записи → used_record_ids (чтобы не предлагать её повторно)
        - f_record сбрасывается для следующего выбора
        
        Args:
            manager: DialogManager
        """
        
        dialog_data = manager.dialog_data
        
        cls._append_to_dialog_list(manager, 'games_out', dialog_data.get('f_record'))
        cls._append_to_dialog_list(manager, 'used_record_ids', dialog_data.get('record_id'))
        
        dialog_data['f_record'] = None
        dialog_data['record_id'] = None
        
    
    @classmethod
    def add_game_in(cls, manager: DialogManager) -> None:
        """
        Добавляет введённую игру во входящие (games_in)
        
        Args:
            manager: DialogManager
        """
        
        cls._append_to_dialog_list(manager, 'games_in', manager.dialog_data.get('game_name'))
    
    @staticmethod
    def _append_to_dialog_list(manager: DialogManager, key: str, value: Any) -> None:
        """
        Добавляет значение в список dialog_data[key]
        Если списка ещё нет — создаёт его
        
        Args:
            manager: DialogManager
            key: ключ списка в dialog_data
            value: добавляемое значение
        """
        
        manager.dialog_data.setdefault(key, []).append(value)

    @classmethod
    async def apply_swap(
        cls,
        manager: DialogManager,
        used_record_ids: list[int],
        new_record_ids: list[int],
    ) -> list[str]:
        """
        Применяет обмен к записям и возвращает отформатированные тексты.

        Для отдаваемых записей (used_record_ids):
            - статус меняется на SOLD
            - привязывается строка обмена

        Для получаемых записей (new_record_ids):
            - привязывается строка обмена (без смены статуса)

        Args:
            manager: DialogManager
            used_record_ids: ID записей, которые отдаются
            new_record_ids: ID записей, которые получаются

        Returns:
            Список отформатированных записей для вывода пользователю
        """
        swap_text = f"{', '.join(map(str, used_record_ids))} - {', '.join(map(str, new_record_ids))}"

        data_for_used_records = {
            'status': RecordStatus.SOLD.value,
            'swap': swap_text,
            'sold_at' : datetime.now(timezone.utc)
        }
        
        u_used_records = await cls.update_many_records(manager, used_record_ids, **data_for_used_records)

        texts = await cls.format_many_records(
            manager,
            [record.id for record in u_used_records]
        )

        data_for_new_records = {'swap': swap_text}
        
        u_new_records = await cls.update_many_records(manager, new_record_ids, **data_for_new_records)

        texts += await cls.format_many_records(
            manager,
            [record.id for record in u_new_records]
        )

        return texts
        
        