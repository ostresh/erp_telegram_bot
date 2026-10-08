from typing import Any, List

from aiogram_dialog import DialogManager

from app.core.db.models import Record
from app.core.db.unit_of_work import UnitOfWork
from app.core.service import GameService, RecordService
from app.interfaces.bot.utils.formatter import MessageFormatter


class RecordOperationsMixin:
    """CRUD и форматирование записей Record."""

    @staticmethod
    async def format_record(manager: DialogManager, record_id: int) -> str:
        """
        Получает Record по id и форматирует его.

        Загружает запись вместе со связанными объектами
        (игра, транзакция, оптовый заказ) и форматирует в HTML
        для отправки в Telegram.

        Args:
            manager: DialogManager
            record_id: id записи

        Returns:
            str: отформатированная строка записи в HTML
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            service = RecordService(session)
            record = await service.get_by_id_with_relations(record_id)

        return MessageFormatter.format_record(record)

    @staticmethod
    async def format_many_records(manager: DialogManager, record_ids: List[int], chunk_size: int = 7):
        """
        Получает Record по id и форматирует его.

        Загружает запись вместе со связанными объектами
        (игра, транзакция, оптовый заказ) и форматирует в HTML
        для отправки в Telegram.

        Args:
            manager: DialogManager
            record_id: id записи

        Returns:
            str: отформатированная строка записи в HTML
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            service = RecordService(session)
            records = await service.get_many_by_ids_with_relations(record_ids)

        return MessageFormatter.format_many_records(records, chunk_size)
    
    @staticmethod
    async def set_record_in_dialog(
        manager: DialogManager,
        record_id: int,
        f_record: str,
    ) -> None:
        """
        Добавляет переменные f_record и record_id в dialog_data.

        Используется для предпросмотра выбранной записи в окне.

        Побочные эффекты:
            - Записывает 'record_id' в manager.dialog_data
            - Записывает 'f_record' в manager.dialog_data
            - Вызывает manager.update() для перерисовки окна

        Args:
            manager: DialogManager
            record_id: id записи
            f_record: отформатированная строка записи
        """
        manager.dialog_data['record_id'] = record_id
        manager.dialog_data['f_record'] = f_record.strip()
        await manager.update()

    @staticmethod
    async def update_record(
        manager: DialogManager,
        record_id: int,
        **data,
    ) -> Record:
        """
        Обновляет один Record.

        Args:
            manager: DialogManager
            record_id: id записи
            data: словарь с полями для обновления (например, {'status': 'sold'})

        Returns:
            Record: обновлённый объект записи
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            service = RecordService(session)
            u_record = await service.update(record_id, **data)

        return u_record

    @staticmethod
    async def update_many_records(
        manager: DialogManager,
        record_ids: List[int],
        **data,
    ) -> List[Record]:
        """
        Обновляет несколько Record одинаковыми данными.

        Используется, когда нужно применить одно изменение
        к группе записей (например, при обмене дисков).

        Все записи обновляются в рамках одной сессии.

        Args:
            manager: DialogManager
            record_ids: список id записей для обновления
            data: словарь с одинаковыми для всех записей полями

        Returns:
            List[Record]: список обновлённых объектов записей
        """
        uow: UnitOfWork = manager.middleware_data["uow"]
        u_records = []

        async with uow() as session:
            service = RecordService(session)
            for record_id in record_ids:
                u_record = await service.update(record_id, **data)
                u_records.append(u_record)

        return u_records

    @staticmethod
    async def create_record(manager: DialogManager, **data) -> Record:
        """
        Создаёт Record.

        Args:
            manager: DialogManager
            data: словарь с полями новой записи (например, {'game_id': 1, 'status': 'available'})

        Returns:
            Record: созданный объект записи
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            service = RecordService(session)
            n_record = await service.create(Record(**data))

        return n_record

    @staticmethod
    async def create_record_from_game_name(
        manager: DialogManager,
        game_name: str,
        **data: Any,
    ) -> Record:
        """
        Создаёт Record по названию игры.

        Автоматически подставляет:
            - game_id: id игры из таблицы игр
            - price_selling: цена продажи, если такая игра уже есть в наличии
                             (иначе None)

        Используется при добавлении нового товара по названию игры.

        Побочные эффекты:
            Создаёт новую запись в БД

        Args:
            manager: DialogManager
            game_name: название игры
            data: дополнительные поля записи (например, {'status': 'available'})

        Returns:
            Record: созданный объект записи

        Raises:
            Игра должна существовать в БД, иначе будет ошибка получения
        """
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            game_service = GameService(session)
            record_service = RecordService(session)

            price_selling = await record_service.get_price_selling_for_game_in_available(
                game_name=game_name,
            )
            game = await game_service.get_by_name(game_name=game_name)

            record = Record(
                game_id=game.id,
                price_selling=price_selling,
                **data,
            )
            new_record = await record_service.create(record)

        return new_record

    @staticmethod
    async def create_records_from_game_names(
        manager: DialogManager,
        game_names: list[str],
        **data: Any,
    ) -> List[Record]:
        """
        Создаёт несколько Record по названиям игр.

        Для каждой игры автоматически подставляет:
            - game_id: id игры из таблицы игр
            - price_selling: цена продажи, если такая игра уже есть в наличии

        Все записи создаются в рамках одной сессии.
        Используется при массовом добавлении товаров (например, в обмене дисков).

        Побочные эффекты:
            Создаёт несколько новых записей в БД

        Args:
            manager: DialogManager
            game_names: список названий игр
            data: дополнительные поля, одинаковые для всех записей

        Returns:
            List[Record]: список созданных объектов записей

        Raises:
            Все игры должны существовать в БД, иначе будет ошибка получения
        """
        new_records = []
        uow: UnitOfWork = manager.middleware_data["uow"]

        async with uow() as session:
            game_service = GameService(session)
            record_service = RecordService(session)

            for game_name in game_names:
                price_selling = await record_service.get_price_selling_for_game_in_available(
                    game_name=game_name,
                )
                game = await game_service.get_by_name(game_name=game_name)

                record = Record(
                    game_id=game.id,
                    price_selling=price_selling,
                    **data,
                )
                new_records.append(await record_service.create(record))

        return new_records
    
    @staticmethod
    async def delete_record(manager: DialogManager, record_id: int) -> bool:
        """
        Удаление строки
        
        Args:
            manager: DialogManager,
            record_id: id записи
        
        Returns:
            bool удалена ли строка
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = RecordService(session)
            is_deleted = await service.delete(record_id)
            
        return is_deleted
    
    @staticmethod
    async def get_record_by_id(manager: DialogManager, record_id: int) -> Record:
        """
        Получение записи по id
        
        Args:
            manager: DialogManager,
            record_id: id записи
        
        Returns:
            Record
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = RecordService(session)
            record = await service.get_by_id(record_id)
            
        return record
    
    @staticmethod
    async def is_record_exists(manager: DialogManager, record_id: int) -> bool:
        """
        Существует ли record
        
        Args:
            manager: DialogManager,
            record_id: id записи
        
        Returns:
            bool существует ли
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = RecordService(session)
            record = await service.get_by_id(record_id)
            
        return record
    
    @staticmethod
    async def get_available_records_by_game(manager: DialogManager, game_name: str) -> List[Record]:
        """
        Получение записей, которые в наличии, по игре
        
        Args:
            manager: DialogManager
            game_name: название игры
            
        Returns:
            Список найденных записей
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            record_service = RecordService(session)
            records = await record_service.get_available_by_game(game_name)
        
        used_record_ids: list = manager.dialog_data.get('used_record_ids')
        if used_record_ids:
            records = [r for r in records if r.id not in used_record_ids]
            
        return records
    
    @staticmethod
    async def get_records_in_transit_to_client_by_game(manager: DialogManager, game_name: str) -> List[Record]:
        """
        Получение записей, которые в наличии, по игре
        
        Args:
            manager: DialogManager
            game_name: название игры
            
        Returns:
            Список найденных записей
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            record_service = RecordService(session)
            records = await record_service.get_in_transit_to_client_by_game(game_name)
            
        return records
        