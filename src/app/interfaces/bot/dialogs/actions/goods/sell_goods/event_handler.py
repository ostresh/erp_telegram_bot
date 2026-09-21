from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select, Button
from aiogram_dialog.widgets.input import TextInput

from app.core.db.unit_of_work import UnitOfWork
from app.core.service import GameService, RecordService, MenuService
from app.core.db.statuses import RecordStatus
from app.core.utils import MessageFormatter, schedule_message_for_deletion
from app.interfaces.bot.utils.emoji import Emoji

from .states import SellGoodsSG

import logging

logger = logging.getLogger(__name__)

class SellGoodsEventHandler:
    
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
        
        Если одна игра доступна, сразу формируется строка для вывода
        Чтобы пользователь не выбирал один id из списка
        
        Перед выводом удаляется сообщение (ввод игры) пользователя.
        """
        
        manager.dialog_data['game'] = text
        manager.dialog_data['emoji_game'] = Emoji.GAME
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            game_service = GameService(session)
            
            is_exists = await game_service.is_game_exists(text.strip())
            
        if not is_exists:
            error_message = await message.answer(
                f'❌ Игра {text} не найдена.\n'
                'Попробуйте еще раз'
            )
            await schedule_message_for_deletion(error_message)
            return
        
        async with uow() as session:
            record_service = RecordService(session)
            
            records = await record_service.get_available_by_game(text)
            
            if len(records) == 1:
                record = await record_service.get_by_id_with_relations(records[0].id)
                f_record = MessageFormatter.format_record(record)
                
                manager.dialog_data['f_record'] = f_record.strip()
                manager.dialog_data['record_id'] = record.id
                
                await message.delete()
                await manager.switch_to(SellGoodsSG.receive_method, show_mode=ShowMode.EDIT)
                return
            
        logger.info(f"Game '{text}' found, proceeding to next step")
        
        await message.delete()
        
        await manager.next(show_mode=ShowMode.EDIT)
    
    @staticmethod
    async def on_price_sold_typed(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        text: int,
    ) -> None:
        """
        Обработчик ввода цены продажи
        
        После ввода обновляется объект Record
        
        Объект форматируется и сразу выводится
        
        Перенаправляется в главное меню
        """
        
        price_sold = text
        receive_type =  manager.dialog_data['receive_type']
        record_id = manager.dialog_data['record_id']
        
        status = (
            RecordStatus.SOLD.value 
            if receive_type == 'local' 
            else RecordStatus.IN_TRANSIT_TO_CLIENT.value
        )
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        data = {
            'price_sold'  : price_sold,
            'status' : status
        }
        
        try:
            async with uow() as session:
                record_service = RecordService(session)
                menu_service = MenuService(session)
                            
                u_record = await record_service.update(record_id, **data)
                u_record_with_relations = await record_service.get_by_id_with_relations(u_record.id)
                
                main_menu = await menu_service.get_menu('main')
                
        except Exception:
            await schedule_message_for_deletion(
                await message.answer('❌ Ошибка при сохранении в БД')
            )
            return
            
        formatted_record = MessageFormatter.format_record(u_record_with_relations)
        
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
        
    @staticmethod
    async def on_record_id_selected(
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str,
    ):
        """
        Обработчик выбора ID записи
        
        Обновляет сообщение и выводит отформатированный Record
        """
        
        await callback.answer()
        
        uow: UnitOfWork = manager.middleware_data["uow"]
        
        async with uow() as session:
            service = RecordService(session)
            
            record = await service.get_by_id_with_relations(int(item_id))
            f_record = MessageFormatter.format_record(record)
        
        manager.dialog_data['record_id'] = int(item_id)    
        manager.dialog_data['f_record'] = f_record.strip()
        
        logger.info(f'Select message updated with record id: {int(item_id) }')
        
        await manager.update()
        
        
        
    @staticmethod
    async def on_record_id_switch_to(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ):
        """Переход к следующему шагу, если выбран record"""
        
        if 'record_id' not in manager.dialog_data:
            logger.info(f'User dont select record id')
            await callback.answer("⚠️ Сначала выберите ID записи!", show_alert=True)
            return
        
        logger.info(f"Selected record id: {manager.dialog_data['record_id']}")
        
        await manager.switch_to(SellGoodsSG.receive_method)