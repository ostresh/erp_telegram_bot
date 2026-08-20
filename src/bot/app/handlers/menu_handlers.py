from aiogram import Router,F
from aiogram.types import CallbackQuery
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import asyncio
from aiogram.fsm.context import FSMContext
from services.menu_services import *
from src.bot.app.callbacks.callbacks import MenuCB
from services.menu_services import *

router = Router()

@router.callback_query(MenuCB.filter(F.title == 'back'))
async def back_handler(callback: CallbackQuery, callback_data: MenuCB, state: FSMContext):
    """Обработчик inline кнопки '← Назад' """
    
    data = await state.get_data()

    if data.get('delete_message_ids'):
        bot = callback.message.bot
        data = await state.get_data()
        delete_message_ids = data.get('delete_message_ids')
        await bot.delete_messages(
            chat_id=callback.message.chat.id,
            message_ids=delete_message_ids
        )
    
    await state.clear()
    await callback.answer(show_alert=False)
    back_dict = await back_menu(callback_data.path)
    await callback.message.edit_text(text=back_dict['text'],
        reply_markup=back_dict['kb'])
    

@router.callback_query(MenuCB.filter(F.path.startswith('main')))
async def menu_handler(callback: CallbackQuery, callback_data: MenuCB, state: FSMContext):
    """Универсальный обработчик меню"""
    
    data = await state.get_data()

    if data.get('delete_message_ids'):
        bot = callback.message.bot
        data = await state.get_data()
        delete_message_ids = data.get('delete_message_ids')
        await bot.delete_messages(
            chat_id=callback.message.chat.id,
            message_ids=delete_message_ids
        )
        
    await callback.answer(show_alert=False)
    menu = await create_menu(callback_data.path)
    await callback.message.edit_text(
        text=menu['text'],
        reply_markup=menu['kb']
    )
    await state.clear()
        
