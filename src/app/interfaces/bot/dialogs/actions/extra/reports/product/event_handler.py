from datetime import datetime
from typing import ClassVar

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput

from app.interfaces.bot.dialogs.common.event_handler import CommonEventHandler
from app.interfaces.bot.dialogs.core import handle_db_errors
from app.interfaces.bot.utils.message import schedule_message_for_deletion

from .states import ProductReportSG
from .flow import ProductReportFlow

class ProductReportEventHandler(CommonEventHandler):
    """
    Обработчик для product_report
    Наследуется от базового обработчика
    
    Переопределяет:
        - Flow: ProductReportFlow
        - States: ProductReportSG
    """
    flow: ClassVar[type[ProductReportFlow]] = ProductReportFlow
    states: ClassVar[type[ProductReportSG]] = ProductReportSG
    
    @classmethod
    @handle_db_errors
    async def on_date_input(
        cls, 
        message: Message, 
        widget: TextInput, 
        manager: DialogManager, 
        text: str
    ):
        """Выгрузка отчета по движению товаров"""
        
        manager.show_mode = ShowMode.DELETE_AND_SEND
        
        try:
            period = [part.strip() for part in text.split(' - ')]
                
            start = datetime.strptime(period[0], '%d.%m.%Y')
            end = datetime.strptime(period[1], '%d.%m.%Y')
        except ValueError:
            await schedule_message_for_deletion(
                await message.answer('❌ Неверный формат периода. Пример: 01.10.2026 - 31.10.2026'),
                manager.middleware_data['uow']
            )
            return

        await message.delete()

        period_start, period_end = period
        
        message_ = await message.answer(
            '⏳ Формирую отчёт...'
        )
        
        await cls.flow.start_report_generation(
            manager,
            chat_id=message.chat.id,
            message_id=message_.message_id,
            period_start_str=period_start,
            period_end_str=period_end
        )
        
        await manager.done()
        
        
        
        
        
        