from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput

from app.core.db.unit_of_work import UnitOfWork
from app.core.service import GameService, RecordService, MenuService
from app.core.db.models import Record
from app.core.db.statuses import RecordStatus
from app.core.utils import MessageFormatter, schedule_message_for_deletion

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
            is_exists = await service.is_game_exists(text.strip())
            
        if not is_exists:
            error_message = await message.answer(
                f'❌ Игра {text} не найдена.\n'
                'Попробуйте еще раз'
            )
            await schedule_message_for_deletion(error_message)
            return
        
        manager.dialog_data['game'] = text
        logger.info(f"Game '{text}' found, proceeding to next step")
        
        
        await message.delete()
        await manager.next(show_mode=ShowMode.EDIT)
        
    @staticmethod
    async def on_price_purchase_typed(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: int,
    ) -> None:
        """
        Обработчик ввода закупочной цены
        
        После ввода создается объект Record
        Price_selling (цена продажи) автоматически устанавливается,
        Если:
            Уже есть эта игра с ценой для продажи
            Игра есть в наличии
        
        Объект форматируется и сразу выводится
        
        Перенаправляется в главное меню
        """
        
        price_purchase = text
        receive_type =  manager.dialog_data['receive_type']
        game = manager.dialog_data['game']
        
        status = (
            RecordStatus.AVAILABLE.value 
            if receive_type == 'local' 
            else RecordStatus.IN_TRANSIT_TO_ME.value
        )
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        
        try:
            async with uow() as session:
                game_service = GameService(session)
                record_service = RecordService(session)
                menu_service = MenuService(session)
                
                price_selling = await record_service.get_price_selling_for_game_in_available(game_name=game)
                
                game = await game_service.get_by_name(game_name=game)
                            
                record = Record(
                    game_id = game.id,
                    price_purchase = price_purchase,
                    price_selling = price_selling,
                    status = status
                )
                
                new_record = await record_service.create(record)
                new_record_with_relations = await record_service.get_by_id_with_relations(new_record.id)
                
                main_menu = await menu_service.get_menu('main')
        except Exception:
            await schedule_message_for_deletion(
                await message.answer('❌ Ошибка при сохранении в БД')
            )
            return
            
        formatted_record = MessageFormatter.format_record(new_record_with_relations)
        
        bot_message_id = manager.current_stack().last_message_id
        
        await message.delete()
        
        message_to_delete = await message.bot.edit_message_text(
            text=formatted_record,
            message_id=bot_message_id,
            chat_id=message.chat.id
        )
        
        await schedule_message_for_deletion(message_to_delete, uow)
        
        await manager.done()
        
        await message.answer(
            text = main_menu.text,
            reply_markup=main_menu.keyboard
        )