from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.input import TextInput

from app.db.unit_of_work import UnitOfWork
from app.service import GameService, RecordService, MenuService
from app.db.models import Record
from app.db.statuses import RecordStatus
from app.utils import MessageFormatter, schedule_message_for_deletion

import logging

logger = logging.getLogger(__name__)

class BuyGoodsEventHandler:
    
    @staticmethod
    async def on_game_typed(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: str,
    ) -> None:
        """
        Обработчик успешного ввода названия игры.
        
        Также здесь проводится проверка, существует ли игра в БД.
        
        Перед выводом удаляется сообщение (ввод игры) пользователя.
        """
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = GameService(session)
            is_exists = service.is_game_exists(text.strip())
            
        if not is_exists:
            await message.answer(
                f'❌ Игра {text} не найдена.\n'
                'Попробуйте еще раз'
            )
            return
        
        manager.dialog_data['game'] = text
        logger.info(f"Game '{text}' found, proceeding to next step")
        
        
        await message.delete()
        await manager.next(show_mode=ShowMode.EDIT)
    
    @staticmethod    
    async def on_receive_method_selected(
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str,
    ) -> None:
        """
        Обработчик выбора метода продажи товара
        (локально или с доставкой)
        """
        
        manager.dialog_data['receive_type'] = item_id
        
        receive_title = manager.dialog_data['receive_methods_map'][item_id]
        manager.dialog_data['receive_title'] = receive_title
        
        logger.info(f"Receive method {item_id}, proceeding to next step")
        
        await manager.next(show_mode=ShowMode.EDIT)
        
    
    @staticmethod
    async def on_price_purchase_typed(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: str,
    ) -> None:
        """
        Обработчик ввода закупочной цены
        
        После ввода создается объект Record
        Форматируется и сразу выводится
        
        Перенаправляется в главное меню
        """
        
        price_purchase = text
        receive_type =  manager.dialog_data['receive_type']
        game = manager.dialog_data['game']
        
        status = RecordStatus.AVAILABLE.value if receive_type == 'local' else RecordStatus.IN_TRANSIT_TO_ME.value
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            game_service = GameService(session)
            record_service = RecordService(session)
            menu_service = MenuService(session)
            
            game = await game_service.get_by_name(game_name=game)
                        
            record = Record(
                game_id = game.id,
                price_purchase = price_purchase,
                status = status
            )
            
            new_record = await record_service.create(record)
            new_record_with_relations = await record_service.get_by_id_with_relations(new_record.id)
            
            main_menu = await menu_service.get_menu('main')
            
        formatted_record = MessageFormatter.format_record(new_record_with_relations)
        
        bot_message_id = manager.current_stack().last_message_id
        
        await message.delete()
        
        await message.bot.delete_message(
            message_id=bot_message_id,
            chat_id=message.chat.id
        )
        
        from aiogram_dialog import ShowMode
        await manager.done(show_mode=ShowMode.NO_UPDATE)
        await manager.close_manager()
        
        message_to_delete = await message.answer(
            text=formatted_record
        )
        
        await schedule_message_for_deletion(message_to_delete, uow)
        
        
        await message.answer(
            text = main_menu.text,
            reply_markup=main_menu.keyboard
        )
        
        
        
        
        
        
        
        
                
        
        
        
        
        