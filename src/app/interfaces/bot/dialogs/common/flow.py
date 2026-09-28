from typing import List, Union

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager

from app.core.db.models import Record
from app.core.db.unit_of_work import UnitOfWork
from app.core.service import MenuService, GameService, RecordService
from app.core.service.menu.schemas import MenuConfig
from app.core.utils import schedule_message_for_deletion
from app.interfaces.bot.utils.formatter import MessageFormatter


class CommonFlow:
    """
    Базовый Flow
    
    Подклассы переопределяют:
        get_records: получениие записей со своей стратегией поиска
    """
    
    @classmethod
    async def get_records(cls, manager: DialogManager) -> List[Record]:
        """
        Получение записей.

        Переопределяется в каждом диалоговом Flow со своей стратегией поиска.
        """
        
        raise NotImplementedError(
            f"{cls.__name__} must implement get_records"
        )
    
    @staticmethod
    async def is_game_exists(manager: DialogManager, game_name: str) -> bool:
        """
        Проверка, существует ли игра в списке
        Если не существует:
            выводится сообщение пользователю,
            просит повторный ввод
            
        Args:
            manager: DialogManager,
            game_name: название игры
            
        Returns:
            bool существует ли игра
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
                
        async with uow() as session:
            game_service = GameService(session)
            is_exists = await game_service.is_game_exists(game_name)
            
        if not is_exists:
            manager.dialog_data['game_error'] = f'Игра "{game_name}" не найдена. Попробуйте ещё раз'
            return False
        
        return True
    
    @staticmethod
    async def get_main_menu(manager: DialogManager) -> MenuConfig:
        """
        Создает MenuConfig для главного меню
        
        Args:
            manager: DialogManager
            
        Returns:
            MenuConfig с клавиатурой
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = MenuService(session)
            main_menu = await service.get_menu('main')
        
        return main_menu
    
    @staticmethod
    async def get_back_menu(manager: DialogManager, path: str) -> MenuConfig:
        """
        Создает MenuConfig для предыдущего меню
        
        Args:
            manager: DialogManager
            path: текущий путь
            
        Returns:
            MenuConfig с клавиатурой
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = MenuService(session)
            main_menu = await service.get_back_menu(path)
        
        return main_menu
    
    @classmethod
    async def finish_dialog_with_result(
        cls,
        manager: DialogManager, 
        text: str) -> None:
        """
        Завершает диалог и отправляет результат пользователю
        С удаляемым сообщением результата
        И отправляет главное меню в чат
        
        Args:
            manager: DialogManager
            text: текст сообщения
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        main_menu = await cls.get_main_menu(manager)
        
        
        event: Union[Message, CallbackQuery] = manager.event
        
        if isinstance(event, CallbackQuery):
            await event.answer()
            
            await schedule_message_for_deletion(
                await event.message.edit_text(
                    text = text,
                ), uow
            )
            
            await event.message.answer(
                text = main_menu.text,
                reply_markup=main_menu.keyboard
            )
            
        elif isinstance(event, Message):
            await event.delete()
            
            last_message_id_ = manager.current_stack().last_message_id
            
            await schedule_message_for_deletion(
                await event.bot.edit_message_text(
                    text = text,
                    message_id=last_message_id_,
                    chat_id=event.chat.id
                ), uow
            )
            
            await event.answer(
                text = main_menu.text,
                reply_markup=main_menu.keyboard
            )
        
        await manager.done()
        
    @staticmethod
    async def is_record_id_selected(callback: CallbackQuery, manager: DialogManager) -> bool:
        """
        Проверяет, выбран ли record_id
        
        Если нет:
            Выдает предупреждение, что record_id не выбран
            
        Args:
            callback: CallbackQuery,
            manager: DialogManager
        """
        
        if 'record_id' not in manager.dialog_data:
            await callback.answer("⚠️ Сначала выберите ID записи!", show_alert=True)
            return False
        
        return True
    
    @staticmethod
    async def set_record_in_dialog_and_format(
        manager: DialogManager, 
        record_id: int, 
    ) -> str:
        """
        Добавляет переменные f_record и record_id в dialog_data
        
        Args:
            manager: DialogManager,
            record_id: id записи.
            
        Returns:
            отформатированная строка
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = RecordService(session)
            record = await service.get_by_id_with_relations(record_id)
        
        f_record = MessageFormatter.format_record(record)
        
        manager.dialog_data['record_id'] = record_id
        manager.dialog_data['f_record'] = f_record.strip()
        
        await manager.update()
        
        return f_record
    
        
    @staticmethod
    async def update_record(manager: DialogManager, record_id: int, **data) -> Record:
        """
        Устанавливает статус для Record
        
        Args:
            manager: DialogManager
            record_id: id записи
            data: словарь с данными
            
        Returns:
            Обновленный объект Record
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = RecordService(session)
            u_record = await service.update(record_id, **data)
            
        return u_record
    
    @staticmethod
    async def create_record(manager: DialogManager, **data) -> Record:
        """
        Создает Record
        
        Args:
            manager: DialogManager
            data: словарь с данными
            
        Returns:
            объект Record
        """
        uow: UnitOfWork = manager.middleware_data["uow"]
                
        async with uow() as session:
            service = RecordService(session)
            n_record = await service.create(Record(**data))
            
        return n_record
        
        