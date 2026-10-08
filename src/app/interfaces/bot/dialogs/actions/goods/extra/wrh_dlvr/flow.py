from typing import Callable, List

from aiogram_dialog import DialogManager

from app.core.db.unit_of_work import UnitOfWork
from app.core.dto.game import AvailableGameDTO
from app.core.service import GameService
from app.core.service.record import RecordService
from app.interfaces.bot.dialogs.common import CommonFlow

import logging

logger = logging.getLogger(__name__)

class WarehouseAndDeliveryFlow(CommonFlow):
    
    @classmethod
    def get_items(cls, manager: DialogManager) -> Callable:
        """
        Получает геттер списка записей/игр в зависимости от действия.

        Args:
            manager: DialogManager

        Returns:
            Callable: функция-геттер

        Raises:
            ValueError: если действие не установлено или неизвестно
        """
        action = manager.start_data.get('callback_action')
        getters = {
            'av-games': cls.get_available_games,
            'av-records': cls.get_available_record_ids,
            'goods_to_client': cls.get_record_ids_in_transit_to_client,
            'goods_to_me': cls.get_record_ids_in_transit_to_me,
        }

        if action not in getters:
            raise ValueError(
                f"Неизвестный или не установленный callback_action: '{action}'. "
                f"Ожидалось одно из: {list(getters.keys())}"
            )

        return getters[action]

    @classmethod
    def formatter(cls, manager: DialogManager) -> Callable:
        """
        Получает форматтер списка записей/игр в зависимости от действия.

        Args:
            manager: DialogManager

        Returns:
            Callable: функция-форматтер

        Raises:
            ValueError: если действие не установлено или неизвестно
        """
        action = manager.start_data.get('callback_action')
        formatters = {
            'av-games': cls.format_many_games,
            'av-records': cls.format_many_records,
            'goods_to_client': cls.format_many_records,
            'goods_to_me': cls.format_many_records,
        }

        if action not in formatters:
            raise ValueError(
                f"Неизвестный или не установленный callback_action: '{action}'. "
                f"Ожидалось одно из: {list(formatters.keys())}"
            )

        return formatters[action]
    
    @staticmethod
    async def get_available_games(manager: DialogManager) -> List[AvailableGameDTO]:
        """
        Получение игр из наличия
        
        Args:
            manager: DialogManager
            
        Returns:
            Список найденных игр
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            game_service = GameService(session)
            games = await game_service.get_available()
            
        return games
    
    @staticmethod
    async def get_available_record_ids(manager: DialogManager) -> List[int]:
        """
        Получение записей из наличия
        
        Args:
            manager: DialogManager
            
        Returns:
            Список найденных записей
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            record_service = RecordService(session)
            records = [record.record.id for record in (await record_service.get_available())]
            
        return records
    
    @staticmethod
    async def get_record_ids_in_transit_to_me(manager: DialogManager) -> List[int]:
        """
        Получение записей, которые в пути ко мне
        
        Args:
            manager: DialogManager
            
        Returns:
            Список найденных записей
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            record_service = RecordService(session)
            records = await record_service.get_in_transit_to_me()
            
        return [record.id for record in records]
    
    @staticmethod
    async def get_record_ids_in_transit_to_client(manager: DialogManager) -> List[int]:
        """
        Получение записей, которые в пути к клиенту
        
        Args:
            manager: DialogManager
            
        Returns:
            Список найденных записей
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            record_service = RecordService(session)
            records = await record_service.get_in_transit_to_client()
            
        return [record.id for record in records]
        
        
    
        
        