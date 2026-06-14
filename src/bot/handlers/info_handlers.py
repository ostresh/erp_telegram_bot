from aiogram import Router,F
from aiogram.types import Message, CallbackQuery
import sys
import os
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database import Database, db
import asyncio
from states.states import InfoSG
from services.info_services import *
from services.menu_services import create_menu_text, create_menu
from keyboards.inline_keyboards import *
from messages.menu_messages import MenuMessage


router = Router()

@router.callback_query(HandlerCB.filter(F.action == 'get_all_finances'))
async def get_financial_info(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    financy = await get_info_of_financy(db, fields=['__all__'])
    message_ = await callback.message.edit_text(financy)
    menu = await create_menu('main')
    await callback.message.answer(
        text = menu['text'],
        reply_markup=menu['kb'],
    )
    
    delete_message_ids = []
    delete_message_ids.append(message_.message_id)
    await state.update_data(delete_message_ids=delete_message_ids)





@router.callback_query(HandlerCB.filter(F.action == 'delivery_to_me'))
async def delivery_to_me_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    await callback.message.delete()
    
    records_delivery_to_me, data_query = await get_records_delivery_to_me(db)
    
    delete_message_ids = []
    
    messages = [await callback.message.answer(item, parse_mode='HTML') for item in records_delivery_to_me]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])

@router.callback_query(HandlerCB.filter(F.action == 'delivery_to_client'))
async def delivery_to_client_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    await callback.message.delete()
    
    records_delivery_to_client, data_query = await get_records_delivery_to_client(db)
    
    delete_message_ids = []
    
    messages = [await callback.message.answer(item, parse_mode='HTML') for item in records_delivery_to_client]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])





@router.callback_query(HandlerCB.filter(F.action == 'records_by_interval'))
async def records_by_interval_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'info', 'records', 'records_by_interval'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.INTERVAL_ID} Введите интервал (через "-")')
    
    message_ = await callback.message.edit_text(
        text = text,
        reply_markup=BACK_KB
    )
    
    await state.set_state(InfoSG.interval_insert_interval_state)
    await state.update_data(message_id = message_.message_id)
    
@router.message(StateFilter(InfoSG.interval_insert_interval_state))
async def records_by_interval_2_handler(message: Message, state: FSMContext):
    
    data = await state.get_data()
    message_id = data.get('message_id')
    
    interval_id = message.text.strip()
    
    interval_records, data_query = await get_records_from_interval_id(db, interval_id)
    
    await message.delete()
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    delete_message_ids = []
    
    messages = [await message.answer(item, parse_mode='HTML') for item in interval_records]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])





@router.callback_query(HandlerCB.filter(F.action == 'av_for_me'))
async def av_for_me_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    await callback.message.delete()
    
    records_av_for_me, data_query = await get_av_records_for_me(db)
    
    delete_message_ids = []
    
    messages = [await callback.message.answer(item, parse_mode='HTML') for item in records_av_for_me]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])
    
@router.callback_query(HandlerCB.filter(F.action == 'av_for_client'))
async def av_for_client_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    await callback.message.delete()
    
    records_av_for_client, data_query = await get_av_records_for_client(db)
    
    delete_message_ids = []
    
    messages = [await callback.message.answer(item, parse_mode='HTML') for item in records_av_for_client]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])
    
@router.callback_query(HandlerCB.filter(F.action == 'av_by_records'))
async def av_by_records_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    await callback.message.delete()
    
    records_av, data_query = await get_av_records(db)
    
    delete_message_ids = []
    
    messages = [await callback.message.answer(item, parse_mode='HTML') for item in records_av]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])




@router.callback_query(HandlerCB.filter(F.action == 'one_bulk_order_by_id'))
async def one_bulk_order_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    all_bulk_orders, data_all_bulk_orders = await get_all_bulk_orders(db)
    
    all_id_data_bulk_orders = list(map(lambda item: str(item.get('id')), data_all_bulk_orders))[::-1]
    
    text = await create_menu_text(['main', 'info', 'bulk_order', 'one_bulk_order_by_id'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.ID} Выберите ID оптового заказа')
    
    inline_kb = await inline_kb_factory(all_id_data_bulk_orders, 'equal')
    
    await callback.message.edit_text(
        text = text,
        reply_markup=inline_kb
    )
    
    await state.set_state(InfoSG.bulk_orders_output_state)

@router.callback_query(StateFilter(InfoSG.bulk_orders_output_state))
async def one_bulk_order_main_handler(callback: CallbackQuery, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    bulk_order_id = int(callback.data)
    
    delete_message_ids = []
    
    await callback.message.delete()
    
    bulk_order, bulk_order_data = await get_one_bulk_order_from_id(db, bulk_order_id)
    
    interval_records_id = bulk_order_data[0].get('interval_records_id')
    
    records, records_data = await get_records_from_interval_id(db, interval_records_id)
    records_messages = [await callback.message.answer(item, parse_mode='HTML') for item in records]
    delete_message_ids += list(map(lambda item: item.message_id, records_messages))
    
    bulk_order_message = [await callback.message.answer(item, parse_mode='HTML') for item in bulk_order]
    delete_message_ids += list(map(lambda item: item.message_id, bulk_order_message))
    
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])




@router.callback_query(HandlerCB.filter(F.action == 'bulk_orders_come_to_me'))
async def bulk_orders_delivery_to_me_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    await callback.message.delete()
    
    bulk_orders_delivery_to_me, data_query = await get_bulk_orders_delivery_to_me(db)
    
    delete_message_ids = []
    
    messages = [await callback.message.answer(item, parse_mode='HTML') for item in bulk_orders_delivery_to_me]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])
    
    

@router.callback_query(HandlerCB.filter(F.action == 'all_bulk_orders'))
async def bulk_orders_delivery_to_me_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    await callback.message.delete()
    
    all_bulk_orders, data_query = await get_all_bulk_orders(db)
    
    delete_message_ids = []
    
    messages = [await callback.message.answer(item, parse_mode='HTML') for item in all_bulk_orders]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])


