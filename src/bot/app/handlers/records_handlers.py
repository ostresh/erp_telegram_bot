from aiogram import Router,F
from aiogram.types import Message, CallbackQuery
import sys
import os
from aiogram.filters import StateFilter
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.bot.database import Database, db
import asyncio
from utils.utils import get_today, create_new_id_for_records
from src.bot.app.states.states import RecordsSG
from services.info_services import *
from services.records_services import *
from src.bot.app.keyboards.inline_keyboards import *
from src.bot.app.keyboards.reply_keyboards import *
from services.menu_services import create_menu_text, create_menu
from src.bot.app.messages.menu_messages import MenuMessage
from .menu_handlers import create_menu
from src.bot.app.callbacks.callbacks import HandlerCB
from src.bot.app.callbacks.callbacks_texts import ACTION_TO_TEXT
from utils.emoji import Emoji


router = Router()
             
             
@router.callback_query(HandlerCB.filter(F.action == 'buy_disc'))
async def buy_game_main_hanlder(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'records', 'buy_discs'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.GAME} Введите название игры')
    
    await callback.message.edit_text(
        text = text,
        reply_markup=SEARCH_INLINE_KB
    )
    
    message_id = callback.message.message_id
    
    await state.set_state(RecordsSG.buy_insert_game_state)
    await state.update_data(message_id = message_id)

@router.message(StateFilter(RecordsSG.buy_insert_game_state))
async def buy_game_2_hanlder(message: Message, state: FSMContext):
    bot = message.bot
    data = await state.get_data()
    message_id = data.get('message_id')
    
    game = message.text.strip()
    
    await state.update_data(game = game)
    await message.delete()
    
    text = f"""
{Emoji.GAME} <b>ИГРА</b>: {game}

{Emoji.LOCAL_OR_DELIVERY} Выберите способ получения:
"""
    await bot.edit_message_text(
    text=text,
    chat_id=message.chat.id,
    message_id=message_id,
    reply_markup=LOCAL_OR_DELIVERY_INLINE_KB
)
    await state.set_state(RecordsSG.buy_insert_get_type_state)
    
@router.callback_query(HandlerCB.filter(), StateFilter(RecordsSG.buy_insert_get_type_state))
async def buy_game_3_hanlder(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    data = await state.get_data()
    game = data.get('game')
    await state.update_data(come_type = callback_data.action)
    
    text = f"""
{Emoji.GAME} <b>ИГРА</b>: {game}
•<b>{ACTION_TO_TEXT.get(callback_data.action)} </b>

Введите:
{Emoji.PRICE_BUY} <b>Расходы</b>
{Emoji.PRICE_SELL} <b>Цену для продажи</b>
{Emoji.COMMENT} <b>Комментарий</b> (необязательно)"""
    
    await callback.message.edit_text(
        text=text,
        reply_markup=BACK_KB
    )
    
    await state.set_state(RecordsSG.buy_insert_data_state)

@router.message(StateFilter(RecordsSG.buy_insert_data_state))
async def buy_game_4_hanlder(message: Message, state: FSMContext):
    
    bot = message.bot
    
    data = await state.get_data()
    game = data.get('game')
    come_type = data.get('come_type')
    message_id = data.get('message_id')
    
    message_text = message.text.strip()
    
    message_text = message.text.strip()
    price_buy = int(message_text.split('\n')[0])
    price_sell = int(message_text.split('\n')[1])
    comment = message_text.split('\n')[2] if len(message_text.split('\n')) == 3 else None
    
    data_db = {
        'id': await create_new_id_for_records(db),
        'buy_at': await get_today(),
        'game_id': game,
        'price_buy': price_buy,
        'price_sell': price_sell,
        'price_sold' : 0,
        'status': 'Да' if come_type == 'local' else 'Едет ко мне',
        'comment': comment
    }
    
    
    await add_records(db, **data_db)
    await message.delete()
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id,
    )
    
    record, data_ = await get_one_record_from_id(db, data_db.get('id'))
    delete_message_ids = [await message.answer(item, parse_mode='HTML') for item in record]
    delete_message_ids = list(map(lambda item: item.message_id, delete_message_ids))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])
    





@router.callback_query(HandlerCB.filter(F.action == 'sell_disc'))
async def sell_game_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'records', 'sell_discs'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.GAME} Выберите игру')
    
    await callback.message.edit_text(
        text = text,
        reply_markup=SEARCH_AV_INLINE_KB
    )
    
    message_id = callback.message.message_id
    
    await state.set_state(RecordsSG.sell_select_records_id_state)
    await state.update_data(message_id = message_id)
    
@router.message(StateFilter(RecordsSG.sell_select_records_id_state))
async def sell_game_2_hanlder(message: Message, state: FSMContext):
    bot = message.bot
    data = await state.get_data()
    message_id = data.get('message_id')
    
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    game = message.text.strip()
    
    await state.update_data(game = game)
    await message.delete()
    
    id_records, id_records_data = await get_specific_games_in_aviable(db, game)
    id_records_data = list(map(lambda item: str(item.get('id')), id_records_data))
    id_records_inline_kb = await inline_kb_factory(id_records_data, row_width='equal')
    
    if len(id_records_data) == 1:
        text = f"""
{id_records[0]}

{Emoji.LOCAL_OR_DELIVERY} Выберите способ получения:
"""
        message_ = await message.answer(
        text=text,
        reply_markup=LOCAL_OR_DELIVERY_INLINE_KB
    )
        await state.set_state(RecordsSG.sell_insert_prices_state)
        await state.update_data(record_id = int(id_records_data[0]))
        await state.update_data(message_id = message_.message_id)
    else:
        
        delete_message_ids = []
    
        av_games, av_games_data = await get_specific_games_in_aviable(db, game)
        
        for item in av_games:
            message_ = await message.answer(item, parse_mode='HTML')
            delete_message_ids.append(message_.message_id)
    
        await state.update_data(delete_message_ids = delete_message_ids)
        
        text = f"""
{Emoji.GAME} <b>ИГРА</b>: {game}

{Emoji.ID} Выберите ID записи:
"""
        main_message = await message.answer(
            text = text,
            reply_markup=id_records_inline_kb
        )
        
        
        await state.set_state(RecordsSG.sell_select_records_id_cb_state)
    
        await state.update_data(message_id = main_message.message_id)
    
@router.callback_query(StateFilter(RecordsSG.sell_select_records_id_cb_state))
async def sell_game_3_cb_handler(callback: CallbackQuery, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    bot = callback.message.bot
    
    data = await state.get_data()
    game = data.get('game')
    delete_message_ids = data.get('delete_message_ids', [])
    delete_message_ids.append(data.get('message_id'))
    
    await bot.delete_messages(
        chat_id=callback.message.chat.id,
        message_ids=delete_message_ids
    )
    
    
    record_id = int(callback.data)
    
    record_message, data_ = await get_one_record_from_id(db, record_id)
    record_message = record_message[0][0:-len(MenuMessage.HORIZONTAL_LINE)+2]
    
    await state.update_data(record_id = int(record_id))
    
    text = f"""
{record_message}
📍🚚 Выберите способ продажи:
"""
    await callback.message.answer(
    text=text,
    reply_markup=LOCAL_OR_DELIVERY_INLINE_KB
)
    await state.set_state(RecordsSG.sell_insert_prices_state)

@router.callback_query(HandlerCB.filter(), StateFilter(RecordsSG.sell_insert_prices_state))
async def sell_game_4_hanlder(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    data = await state.get_data()
    game = data.get('game')
    record_id = data.get('record_id')
    await state.update_data(come_type = callback_data.action)
    
    text = f"""
{Emoji.ID} {record_id}
{Emoji.GAME} <b>ИГРА</b>: {game}
•<b>{ACTION_TO_TEXT.get(callback_data.action)} </b>

Введите:
{Emoji.PRICE_SOLD} <b>Доход</b>"""
    
    message_ = await callback.message.edit_text(
        text=text,
        reply_markup=BACK_KB
    )
    
    await state.set_state(RecordsSG.sell_insert_data_state)
    await state.update_data(message_id = message_.message_id)

@router.message(StateFilter(RecordsSG.sell_insert_data_state))
async def sell_game_5_hanlder(message: Message, state: FSMContext):
    bot = message.bot
    data = await state.get_data()
    
    record_id = int(data.get('record_id'))
    come_type = data.get('come_type')
    message_id = data.get('message_id')
    
    price_sold = int(message.text.strip())
    
    data_db = {
        'id': record_id,
        'sold_at': await get_today(),
        'price_sold': price_sold,
        'status': 'Нет' if come_type == 'local' else 'Едет к покупателю',
    }
    
    
    await update_records(db, **data_db)
    await message.delete()
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id,
    )
    
    await state.clear()
    
    delete_message_ids = []
    
    record, record_data = await get_one_record_from_id(db, data_db.get('id'))
    messages_id = [await message.answer(item, parse_mode='HTML') for item in record]
    delete_message_ids += list(map(lambda item: item.message_id, messages_id))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])
    
    




@router.callback_query(HandlerCB.filter(F.action == 'order_arrived'))
async def order_arrived_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'records', 'order_arrived'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.LOCAL_OR_DELIVERY} Выберите, к кому приехал')
    
    await callback.message.edit_text(
        text = text,
        reply_markup=COME_TOME_OR_CLIENT_INLINE_KB
    )
    
    message_id = callback.message.message_id
    
    await state.set_state(RecordsSG.order_arrived_insert_game_state)
    await state.update_data(message_id = message_id)

@router.callback_query(HandlerCB.filter(), StateFilter(RecordsSG.order_arrived_insert_game_state))
async def order_arrived_2_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):

    await callback.answer(show_alert=False)
    
    arrived_to = callback_data.action
    await state.update_data(arrived_to = arrived_to)
    
    text = f"""
{MenuMessage.HORIZONTAL_LINE}<b>ПРИЕХАЛ:</b> {ACTION_TO_TEXT.get(arrived_to)}

{Emoji.GAME} Выберите игру
    """
    
    if arrived_to == 'to_me':
        message_ = await callback.message.edit_text(
            text = text,
            reply_markup=SEARCH_DELIVERY_TO_ME_INLINE_KB
        )
    else:
        message_ = await callback.message.edit_text(
            text = text,
            reply_markup=SEARCH_DELIVERY_TO_CLIENT_INLINE_KB
        )
        
    await state.set_state(RecordsSG.order_arrived_output_records_state)
    await state.update_data(message_id = message_.message_id)

@router.message(StateFilter(RecordsSG.order_arrived_output_records_state))
async def order_arrived_3_handler(message: Message, state: FSMContext):
    
    data = await state.get_data()
    message_id = data.get('message_id')
    arrived_to = data.get('arrived_to')
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    game = message.text.strip()
    await state.update_data(game = game)
    
    await message.delete()
    
    if arrived_to == 'to_me':
        records, records_ids = await get_specific_games_delivery_to_me_without_bulk_order(db, game)
    else: records, records_ids = await get_specific_games_delivery_to_client(db, game)
    
    delete_message_ids = []
    
    records_messages = [await message.answer(item, parse_mode='HTML') for item in records]
    delete_message_ids += list(map(lambda item: item.message_id, records_messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    records_ids = list(map(lambda item: str(item.get('id')), records_ids))
    
    text = f"""
{Emoji.GAME} <b>ИГРА:</b> {game}
<b>ПРИЕХАЛ:</b> {ACTION_TO_TEXT.get(arrived_to)}

{Emoji.ID} Выберите ID заказа 
    """
    
    inline_kb = await inline_kb_factory(records_ids, 'equal')
    
    message_ = await message.answer(
        text = text,
        reply_markup=inline_kb
    )
    
    await state.set_state(RecordsSG.order_arrived_insert_data_state)
    await state.update_data(delete_message_ids = delete_message_ids, message_ = message_)
    
@router.callback_query(StateFilter(RecordsSG.order_arrived_insert_data_state))
async def order_arrived_3_handler(callback: CallbackQuery, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    data = await state.get_data()
    delete_message_ids = data.get('delete_message_ids')
    arrived_to = data.get('arrived_to')
    delete_message_ids = data.get('delete_message_ids')
    message_ = data.get('message_')
    
    delete_message_ids.append(message_.message_id)
    
    bot = callback.message.bot
    
    await bot.delete_messages(
        chat_id=callback.message.chat.id,
        message_ids=delete_message_ids
    )
    
    data_db = {
        'id' : int(callback.data),
        'status' : 'Да' if arrived_to == 'to_me' else 'Нет'
    }
    
    await update_records(db, **data_db)
    
    await state.clear()
    
    record, data_ = await get_one_record_from_id(db, data_db.get('id'))
    messages = [await callback.message.answer(item, parse_mode='HTML') for item in record]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])
    
    





@router.callback_query(HandlerCB.filter(F.action == 'swap_disc'))
async def swap_disc_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    await callback.message.delete()
    
    delete_message_ids = []
    
    records, data_ = await get_av_records(db)
    
    messages = [await callback.message.answer(item, parse_mode='HTML') for item in records]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    
    text = await create_menu_text(['main', 'records', 'swap'])
    
    text = text.replace(
        MenuMessage.ADDON_TEXT, f"""
{Emoji.ID} Введите ID отдачи (через запятую)
{Emoji.ID} Введите ID получения
                        """)
    
    message_ = await callback.message.answer(
        text = text,
        reply_markup=BACK_KB
    )
    
    
    await state.set_state(RecordsSG.swap_insert_ids_state)
    await state.update_data(message_id = message_.message_id, delete_message_ids = delete_message_ids)
    
@router.message(StateFilter(RecordsSG.swap_insert_ids_state))
async def swap_disc_2_handler(message: Message, state: FSMContext):
    
    data = await state.get_data()
    message_id = data.get('message_id')
    delete_message_ids = data.get('delete_message_ids')
    
    delete_message_ids.append(message_id)
    
    await message.bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=delete_message_ids
    )

    await message.delete()

    swap_ids = message.text.strip().split('\n')
    give_swap_ids = swap_ids[0].split(',')
    received_swap_ids = swap_ids[1].split(',')
    
    records_ids = []
    
    for item in give_swap_ids:
        data_db = {
            'id': int(item.strip()),
            'sold_at' : await get_today(),
            'status' : 'Нет',
            'swap' : ",".join(received_swap_ids)
        }
        await update_records(db, **data_db)
        records_ids.append(int(item.strip()))
        
        
    for item in received_swap_ids:
        data_db = {
            'id': int(item.strip()),
            'swap' : ",".join(give_swap_ids)
        }
        await update_records(db, **data_db)
        records_ids.append(int(item.strip()))
    
    delete_message_ids = []
     
    for id_ in records_ids:
        responce, data_ = await get_one_record_from_id(db, id_)
        records_messages = [await message.answer(item, parse_mode='HTML') for item in responce]
        delete_message_ids += list(map(lambda item: item.message_id, records_messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])
        

        



@router.callback_query(HandlerCB.filter(F.action == 'reserve_disc'))
async def reserve_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'records', 'reserve'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.GAME} Выберите игру') 
    
    message_ = await callback.message.edit_text(
        text = text,
        reply_markup = SEARCH_RESERVE_INLINE_KB
    )
    
    await state.set_state(RecordsSG.reserve_insert_game_state)
    await state.update_data(message_id = message_.message_id)

@router.message(StateFilter(RecordsSG.reserve_insert_game_state))
async def reserve_2_hanlder(message: Message, state: FSMContext):


    await message.delete()
    data = await state.get_data()
    message_id = data.get('message_id')
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )

    game = message.text.strip()
    await state.update_data(game = game)
    
    av_specific_games, id_records = await get_specific_games_for_reserve(db, game)
    
    id_records = list(map(lambda item: str(item.get('id')), id_records))
    
    delete_message_ids = []
    
    if len(id_records) == 1:
        text = f"""
{Emoji.ID} {id_records[0]}
{Emoji.GAME} <b>ИГРА</b>: {game}

{Emoji.RESERVE} Введите имя бронирующего:
"""
        message_ = await message.answer(
        text=text,
        reply_markup=BACK_KB
    )
        await state.set_state(RecordsSG.reserve_insert_name_state)
        await state.update_data(record_id = id_records[0])
        await state.update_data(message_id = message_.message_id)
    else:
        
        for item in av_specific_games:
            message_ = await message.answer(item, parse_mode='HTML')
            delete_message_ids.append(message_.message_id)
            
        
        id_records_inline_kb = await inline_kb_factory(id_records, 'equal')
        
        text = f"""
{Emoji.GAME} <b>ИГРА</b>: {game}

{Emoji.ID} Выберите ID записи:
"""
        main_message = await message.answer(
            text = text,
            reply_markup=id_records_inline_kb
        )
        
        await state.set_state(RecordsSG.reserve_select_id_state)
        await state.update_data(message_id = main_message.message_id)
        
    await state.update_data(delete_message_ids = delete_message_ids)
    
@router.callback_query(StateFilter(RecordsSG.reserve_select_id_state))
async def reserve_3_cb_handler(callback: CallbackQuery, state: FSMContext):
    
    await callback.answer(show_alert=False)
    data = await state.get_data()
    game = data.get('game')
    message_id = data.get('message_id')
    delete_message_ids = data.get('delete_message_ids', [])
    
    await callback.message.bot.delete_messages(
        chat_id=callback.message.chat.id,
        message_ids=delete_message_ids
    )
    
    
    record_id = callback.data
    
    await state.update_data(record_id = record_id)
    
    await state.update_data(record_id = record_id)
    
    text = f"""
{Emoji.ID} {record_id}
{Emoji.GAME} <b>ИГРА</b>: {game}

{Emoji.RESERVE} Введите имя бронирующего:
"""
    message_ = await callback.message.bot.edit_message_text(
    chat_id=callback.message.chat.id,
    message_id=message_id,
    text = text,
    reply_markup=BACK_KB
)       
    await state.set_state(RecordsSG.reserve_insert_name_state)
    await state.update_data(message_id = message_.message_id)

@router.message(StateFilter(RecordsSG.reserve_insert_name_state))
async def reserve_4_hanlder(message: Message, state: FSMContext):
    
    data = await state.get_data()
    message_id = data.get('message_id')
    delete_message_ids = data.get('delete_message_ids', [])
    record_id = data.get('record_id')
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    delete_message_ids.append(message_id)
    
    name = message.text.strip()
    
    await message.delete()
    
    data_db = {
        'id' : int(record_id),
        'reserve': name
    }
    
    await update_records(db, **data_db)
    
    record, data_ = await get_one_record_from_id(db, data_db.get('id'))
    messages = [await message.answer(item, parse_mode='HTML') for item in record]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])
    




@router.callback_query(HandlerCB.filter(F.action == 'change_row_by_id'))
async def change_row_by_id_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'service', 'records', 'change_row_by_id'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.ID} Введите ID строки')
    
    message_ = await callback.message.edit_text(
        text = text,
        reply_markup=BACK_KB
    )
    
    await state.update_data(message_id = message_.message_id)
    await state.set_state(RecordsSG.change_row_by_id_insert_id_state)
    
@router.message(StateFilter(RecordsSG.change_row_by_id_insert_id_state))
async def change_row_by_id_2_hanlder(message: Message, state: FSMContext):
    
    data = await state.get_data()
    message_id = data.get('message_id')
    
    record_id = int(message.text.strip())
    await message.delete()
    await state.update_data(record_id = record_id)
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    delete_message_ids = []
    
    message_ = await message.answer(
        await get_one_row_from_id(db, record_id)
    )
    
    delete_message_ids.append(message_.message_id)
    
    message_ = await message.answer(
        text = '⤵️ Введите новую строку'
    )
    
    delete_message_ids.append(message_.message_id)
    
    await state.update_data(delete_message_ids = delete_message_ids)
    await state.set_state(RecordsSG.change_row_by_id_insert_new_row_state)
    
@router.message(StateFilter(RecordsSG.change_row_by_id_insert_new_row_state))
async def change_row_by_id_2_hanlder(message: Message, state: FSMContext):
    
    data = await state.get_data()
    delete_message_ids = data.get('delete_message_ids')
    
    row = message.text.strip()
    await message.delete()
    
    await message.bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=delete_message_ids
    )
    
    data_db = await create_dataset_for_one_row(row)
    
    await update_records(db, **data_db)
    
    record, data_ = await get_one_record_from_id(db, data_db.get('id'))
    messages = [await message.answer(item, parse_mode='HTML') for item in record]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])
    
    
 
 
    
@router.callback_query(HandlerCB.filter(F.action == 'update_price_for_specific_games'))
async def update_price_for_specific_games_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'service', 'records', 'update_price_for_specific_games'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.GAME} Выберите игру')
    
    await callback.message.edit_text(
        text = text,
        reply_markup=SEARCH_AV_INLINE_KB
    )
    
    message_id = callback.message.message_id
    
    await state.set_state(RecordsSG.update_price_for_specific_games_insert_game_state)
    await state.update_data(message_id = message_id)
    
@router.message(StateFilter(RecordsSG.update_price_for_specific_games_insert_game_state))
async def update_price_for_specific_games_2_hanlder(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    game = message.text.strip()
    await message.delete()
    
    await state.update_data(game = game) 
    
    text = f"""
{Emoji.GAME} <b>ИГРА</b>: {game}

{Emoji.PRICE_SELL} Введите цену для продажи:
"""
    message_ = await message.answer(
        text=text,
        reply_markup=BACK_KB
    )
    
    await state.update_data(message_id = message_.message_id)
    await state.set_state(RecordsSG.update_price_for_specific_games_insert_price_sell_state)
    
@router.message(StateFilter(RecordsSG.update_price_for_specific_games_insert_price_sell_state))
async def update_price_for_specific_games_3_hanlder(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    game = data.get('game')
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    price_sell = int(message.text.strip())
    await message.delete()
    
    await update_price_sell_for_specific_records(db, game, price_sell)
    
    delete_message_ids = []
    
    id_records, id_records_data = await get_specific_games_in_aviable(db, game)
    messages = [await message.answer(item, parse_mode='HTML') for item in id_records]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])
    
    




@router.callback_query(HandlerCB.filter(F.action == 'delete_row_by_id'))
async def delete_row_by_id_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'service', 'records', 'delete_row_by_id'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.ID} Введите ID строки')
    
    await callback.message.edit_text(
        text = text,
        reply_markup=BACK_KB
    )
    
    message_id = callback.message.message_id
    
    await state.set_state(RecordsSG.delete_row_by_id_insert_id_state)
    await state.update_data(message_id = message_id)

@router.message(StateFilter(RecordsSG.delete_row_by_id_insert_id_state))
async def delete_row_by_id_2_hanlder(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    game = data.get('game')
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    id_record = int(message.text.strip())
    await message.delete()
    
    await delete_row(db, id_record)
    
    message_ = await message.answer(
        text = f'{Emoji.ID} Строка {id_record} удалена!'
    )
    
    delete_message_ids = [message_.message_id]
    await state.update_data(delete_message_ids=delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])


        





@router.callback_query(HandlerCB.filter(F.action == 'add_trns_cb'))
async def trns_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    data = await state.get_data()
    
    if data.get('delete_message_ids'):
        bot = callback.message.bot
        data = await state.get_data()
        delete_message_ids = data.get('delete_message_ids')
        await bot.delete_messages(
            chat_id=callback.message.chat.id,
            message_ids=delete_message_ids
        )
    
    trns_list = await get_trns_list(db)
    
    trns_list_without_prefix, prefix = await delete_prefix_from_trns(trns_list)
    
    inline_kb = await inline_kb_factory(trns_list_without_prefix, 1)
    text = await create_menu_text(['main', 'trns'])
    text = text.replace(MenuMessage.ADDON_TEXT, '\n📝 <b>Выберите транзакцию</b>')
    
    await callback.message.edit_text(text=text, reply_markup=inline_kb, parse_mode='HTML')
    await state.set_state(RecordsSG.trns_insert_trns_state)
    await state.update_data(prefix = prefix)
    
@router.callback_query(StateFilter(RecordsSG.trns_insert_trns_state))
async def trns_handler(callback: CallbackQuery, state: FSMContext):
    
    current_state = await state.get_state()
    if current_state is None:
        # Состояние было очищено, пользователь вышел
        menu = await create_menu('main')
        await message.answer(text=menu['text'], reply_markup=menu['kb'])
        return
    
    
    data = await state.get_data()
    prefix = data.get('prefix')
    # Отвечаем Telegram, чтобы индикатор “чекается” исчез
    await callback.answer()

    # Сохраняем выбранный идентификатор
    trns = callback.data
    await state.update_data(trns=trns, prefix = prefix)

    # Переходим к следующему шагу
    await state.set_state(RecordsSG.trns_insert_price_and_comment_state)

    message = await callback.message.edit_text(f"""
{Emoji.TRNS} <b>ТРАНЗАКЦИЯ</b>: {trns}

Введите:
{Emoji.PRICE_BUY} <b>Расходы</b>
{Emoji.PRICE_SOLD} <b>Доходы</b>
{Emoji.COMMENT} <b>Комментарий</b> (необязательно)""",
        parse_mode='HTML',
        reply_markup=BACK_KB
    )
    
    await state.update_data(message = message)

@router.message(StateFilter(RecordsSG.trns_insert_price_and_comment_state))
async def trns_handler(message: Message, state: FSMContext, bot):
    
    data = await state.get_data()
    trns = data.get('trns', 'unknown')
    prefix = data.get('prefix')
    old_message = data.get('message')
    
    text = message.text.strip()
    price_buy = int(text.split('\n')[0])
    price_sold = int(text.split('\n')[1])
    try:
        comment = text.split('\n')[2]
    except:
        comment = None
    
    data_db = {
        'id': await create_new_id_for_records(db),
        'buy_at': await get_today(),
        'sold_at': await get_today(),
        'trns_id': f"{prefix} {trns}",
        'price_buy': price_buy,
        'price_sold': price_sold,
        'status': 'Нет',
        'comment': comment
    }
    
    
    await add_records(db, **data_db)
    await message.delete()
    await bot.delete_message(
        chat_id=old_message.chat.id, 
        message_id=old_message.message_id
    )
    
    delete_message_ids = []
    
    trns_row, data_ = await get_one_record_from_id(db, data_db.get('id'))
    messages = [await message.answer(item, parse_mode='HTML') for item in trns_row]
    delete_message_ids += list(map(lambda item: item.message_id, messages))
    await state.update_data(delete_message_ids=delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])  