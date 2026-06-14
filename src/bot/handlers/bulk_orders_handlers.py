from aiogram import Router,F
from aiogram.types import Message, CallbackQuery
import sys
import os
from aiogram.filters import StateFilter
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database import Database, db
import asyncio
from states.states import BulkOrderSG
from services.bulk_orders_services import *
from services.info_services import *
from aiogram.fsm.context import FSMContext
from keyboards.inline_keyboards import *
from services.menu_services import create_menu_text, create_menu

router = Router()
  
  
@router.callback_query(HandlerCB.filter(F.action == 'new_bulk_order'))
async def new_bulk_order_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'bulk_order', 'new_bulk_order'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'⤵️ Введите CSV')
    
    message_ = await callback.message.edit_text(
        text = text,
        reply_markup=BACK_KB
    )
    
    await state.set_state(BulkOrderSG.new_bulk_order_insert_csv_state)
    await state.update_data(message_id = message_.message_id)
    
@router.message(StateFilter(BulkOrderSG.new_bulk_order_insert_csv_state))
async def new_bulk_order_2_handler(message: Message, state: FSMContext):
    
    data = await state.get_data()
    message_id = data.get('message_id')
    
    csv_string = message.text.strip()
    
    await message.delete()
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    bulk_order_id = await new_bulk_order(db, csv_string)
    
    bulk_order, bulk_order_data = await get_one_bulk_order_from_id(db, bulk_order_id)
    
    interval_records_id = bulk_order_data[0].get('interval_records_id')
    
    delete_message_ids = []
    
    records, records_data = await get_records_from_interval_id(db, interval_records_id)
    records_messages = [await message.answer(item, parse_mode='HTML') for item in records]
    delete_message_ids += list(map(lambda item: item.message_id, records_messages))
    
    bulk_order_message = [await message.answer(item, parse_mode='HTML') for item in bulk_order]
    delete_message_ids += list(map(lambda item: item.message_id, bulk_order_message))
    
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])






@router.callback_query(HandlerCB.filter(F.action == 'add_delivery_to_bulk_order'))
async def add_delivery_to_bulk_order_main_hanlder(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    bulk_orders_delivery_to_me, data_bulk_orders_delivery_to_me = await get_bulk_orders_delivery_to_me(db)
    
    bulk_orders_id_delivery_to_me = list(map(lambda item: str(item.get('id')), data_bulk_orders_delivery_to_me))
    
    if len(bulk_orders_id_delivery_to_me) > 1:
    
        await callback.message.delete()
        
        delete_message_ids = []
        
        messages = [await callback.message.answer(item, parse_mode='HTML') for item in bulk_orders_delivery_to_me]
        delete_message_ids += list(map(lambda item: item.message_id, messages))
        
        text = await create_menu_text(['main', 'bulk_order', 'add_delivery_to_bulk_order'])
        
        text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.ID} Выберите ID оптового заказа')
        
        inline_kb = await inline_kb_factory(bulk_orders_id_delivery_to_me, 'equal')
        
        message_ = await callback.message.answer(
            text = text,
            reply_markup=inline_kb
        )
        
        await state.set_state(BulkOrderSG.add_delivery_to_bulk_order_select_id_state)
        await state.update_data(delete_message_ids = delete_message_ids, message_id = message_.message_id)
    
    
    elif len(bulk_orders_id_delivery_to_me) == 1:
        
        await callback.message.delete()
        
        delete_message_ids = []
        
        messages = [await callback.message.answer(item, parse_mode='HTML') for item in bulk_orders_delivery_to_me]
        delete_message_ids += list(map(lambda item: item.message_id, messages))
        
        text = text=f"""
{Emoji.ORDER_BULK} ОПТОВЫЙ ЗАКАЗ {Emoji.ID} <b>{bulk_orders_id_delivery_to_me[0]}</b>

{Emoji.ORDER_BULK_DELIVERY_COST} Введите стоимость доставки"""

        message_ = await callback.message.answer(
            text = text,
            reply_markup=BACK_KB
        )
        
        await state.set_state(BulkOrderSG.add_delivery_to_bulk_order_insert_price_state)
        await state.update_data(delete_message_ids = delete_message_ids, message_id = message_.message_id, bulk_order_id = bulk_orders_id_delivery_to_me[0])
        
    else:
        message_ = await callback.message.edit_text(
            text = f'{Emoji.ORDER_BULK} Активных заказов нет!'
        )
    
        delete_message_ids = [message_.message_id]
    
        menu = await create_menu('main')
        await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])
        await state.update_data(delete_message_ids = delete_message_ids)

@router.callback_query(StateFilter(BulkOrderSG.add_delivery_to_bulk_order_select_id_state))
async def add_delivery_to_bulk_order_1_handler(callback: CallbackQuery, state: FSMContext):
    
    data = await state.get_data()
    delete_message_ids = data.get('delete_message_ids')
    
    await callback.message.bot.delete_messages(
        chat_id=callback.message.chat.id,
        message_ids=delete_message_ids
    )
    
    await callback.answer(show_alert=False)
    
    bulk_order_id = int(callback.data)
    await state.update_data(bulk_order_id = bulk_order_id)
    
    text=f"""
{Emoji.ORDER_BULK} ОПТОВЫЙ ЗАКАЗ {Emoji.ID} <b>{bulk_order_id}</b>

{Emoji.ORDER_BULK_DELIVERY_COST} Введите стоимость доставки"""
    
    await callback.message.edit_text(
        text=text,
        reply_markup=BACK_KB
    )

    await state.set_state(BulkOrderSG.add_delivery_to_bulk_order_insert_price_state)

@router.message(StateFilter(BulkOrderSG.add_delivery_to_bulk_order_insert_price_state))
async def add_delivery_to_bulk_order_2_hanlder(message: Message, state: FSMContext):
    
    data = await state.get_data()
    delete_message_ids = data.get('delete_message_ids')
    bulk_order_id = data.get('bulk_order_id')
    message_id = data.get('message_id')
    
    delete_message_ids.append(message_id)
    
    delivery_cost = message.text.strip()
    
    await message.delete()
    
    await message.bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=delete_message_ids
    )
    
    await add_delivery_to_bulk_order_from_id(db, int(bulk_order_id), int(delivery_cost))
    
    
    bulk_order, bulk_order_data = await get_one_bulk_order_from_id(db, int(bulk_order_id))
    
    bulk_order_message = [await message.answer(item, parse_mode='HTML') for item in bulk_order]
    delete_message_ids += list(map(lambda item: item.message_id, bulk_order_message))
    
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])
    
    
    
    
    
    
    
    
@router.callback_query(HandlerCB.filter(F.action == 'bulk_order_arrived'))
async def bulk_order_arrived_main_hanlder(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    
    bulk_orders_delivery_to_me, data_bulk_orders_delivery_to_me = await get_bulk_orders_delivery_to_me(db)
    
    bulk_orders_id_delivery_to_me = list(map(lambda item: str(item.get('id')), data_bulk_orders_delivery_to_me))
    
    if len(bulk_orders_id_delivery_to_me) > 1:
    
        await callback.message.delete()
        
        delete_message_ids = []
        
        messages = [await callback.message.answer(item, parse_mode='HTML') for item in bulk_orders_delivery_to_me]
        delete_message_ids += list(map(lambda item: item.message_id, messages))
        
        text = await create_menu_text(['main', 'bulk_order', 'add_delivery_to_bulk_order'])
        
        text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.ID} Выберите ID оптового заказа')
        
        inline_kb = await inline_kb_factory(bulk_orders_id_delivery_to_me, 'equal')
        
        message_ = await callback.message.answer(
            text = text,
            reply_markup=inline_kb
        )
        
        await state.set_state(BulkOrderSG.bulk_order_come_to_me_state)
        await state.update_data(delete_message_ids = delete_message_ids, message_id = message_.message_id)
    
    
    elif len(bulk_orders_id_delivery_to_me) == 1:
        
        await callback.message.delete()
        
        delete_message_ids = []
        
        await bulk_order_arrived_from_id(db, int(bulk_orders_id_delivery_to_me[0]))
        
        bulk_order, bulk_order_data = await get_one_bulk_order_from_id(db, int(bulk_orders_id_delivery_to_me[0]))
    
        bulk_order_message = [await callback.message.answer(item, parse_mode='HTML') for item in bulk_order]
        delete_message_ids += list(map(lambda item: item.message_id, bulk_order_message))
        
        await state.update_data(delete_message_ids = delete_message_ids)
        
        menu = await create_menu('main')
        await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])
        
        
    else:
        
        message_ = await callback.message.edit_text(
            text = f'{Emoji.ORDER_BULK} Активных заказов нет!'
        )
    
        delete_message_ids = [message_.message_id]
    
        menu = await create_menu('main')
        await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])
        await state.update_data(delete_message_ids = delete_message_ids)
        
@router.callback_query(StateFilter(BulkOrderSG.bulk_order_come_to_me_state))
async def bulk_order_arrived_2_hanlder(callback: CallbackQuery, state: FSMContext):
    
    data = await state.get_data()
    delete_message_ids = data.get('delete_message_ids')
    
    await callback.message.bot.delete_messages(
        chat_id=callback.message.chat.id,
        message_ids=delete_message_ids
    )
    
    bulk_order_id = callback.data
    
    await callback.message.delete()
        
    delete_message_ids = []
    
    await bulk_order_arrived_from_id(db, int(bulk_order_id))
    
    bulk_order, bulk_order_data = await get_one_bulk_order_from_id(db, int(bulk_order_id))

    bulk_order_message = [await callback.message.answer(item, parse_mode='HTML') for item in bulk_order]
    delete_message_ids += list(map(lambda item: item.message_id, bulk_order_message))
    
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])
    
    
    



@router.callback_query(HandlerCB.filter(F.action == 'delete_bulk_order_by_id'))
async def delete_bulk_order_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'service', 'bulk_order', 'delete_bulk_order_by_id'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.ID} Введите ID оптового заказа')
    
    message_ = await callback.message.edit_text(
        text = text,
        reply_markup=BACK_KB
    )

    await state.update_data(message_id = message_.message_id)
    await state.set_state(BulkOrderSG.delete_bulk_order_insert_id_state)
    
@router.message(BulkOrderSG.delete_bulk_order_insert_id_state)
async def delete_bulk_order_2_handler(message: Message, state: FSMContext):
    
    data = await state.get_data()
    message_id = data.get('message_id')
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    bulk_order_id =  int(message.text.strip())
    
    await message.delete()
    
    await delete_bulk_order_from_id(db, bulk_order_id)
     
    message_ = await message.answer(
        text = f'❌ Оптовый заказ {bulk_order_id} удален!'
    )
        
    delete_message_ids = [message_.message_id]
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])