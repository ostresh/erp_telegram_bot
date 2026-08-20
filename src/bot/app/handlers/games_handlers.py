from aiogram import Router,F
from aiogram.types import Message, CallbackQuery
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.bot.database import Database, db
import asyncio
from src.bot.app.states.states import GamesListSG
from services.info_services import *
from services.games_services import *
from aiogram.fsm.context import FSMContext
from src.bot.app.callbacks.callbacks import HandlerCB
from src.bot.app.keyboards.inline_keyboards import *
from services.menu_services import create_menu_text, create_menu

router = Router()



@router.callback_query(HandlerCB.filter(F.action == 'add_game_to_games_list'))
async def add_game_to_games_list_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'service', 'games_list', 'add_game_to_games_list'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.GAME} Введите название игры')
    
    message_ = await callback.message.edit_text(
        text = text,
        reply_markup=BACK_KB
    )

    await state.update_data(message_id = message_.message_id)
    await state.set_state(GamesListSG.add_game_to_games_list_insert_name_state)
    
@router.message(GamesListSG.add_game_to_games_list_insert_name_state)
async def add_game_to_games_list_2_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    name = message.text.strip()
    await message.delete()
    
    if not await check_game_in_game_list(db, name):
        
        text = f"""
{Emoji.GAME} <b>ИГРА</b>: {name}

{Emoji.TAGS} Введите теги:
""" 
        message_ = await message.answer(
            text = text,
            reply_markup=BACK_KB
        )
        await state.update_data(name = name, message_id = message_.message_id)
        await state.set_state(GamesListSG.add_game_to_games_list_insert_tags_state)
    else:
        message_ = await message.answer(
            text = '❌ Эта игра уже есть в списке!',
        )
        delete_message_ids = [message_.message_id]
        await state.update_data(delete_message_ids=delete_message_ids)
        
        menu = await create_menu('main')
        await message.answer(text = menu['text'], reply_markup=menu['kb'])
    
@router.message(GamesListSG.add_game_to_games_list_insert_tags_state)
async def add_game_to_game_list_3_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    name = data.get('name')
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    tags = message.text.strip()
    await message.delete()
    
    await add_game_in_game_list(db, name, tags)
    
    if await check_game_in_game_list(db, name):
        text = f"""
✅ Новая игра записана!

{Emoji.GAME} <b>ИГРА</b>: {name}

{Emoji.TAGS} {tags}
""" 
        message_ = await message.answer(
            text = text
        )
        
        delete_message_ids = [message_.message_id]
        await state.update_data(delete_message_ids = delete_message_ids)
        
        menu = await create_menu('main')
        await message.answer(text = menu['text'], reply_markup=menu['kb'])
        
    else:
        text = f"""
❌ Ошибка
""" 
        message_ = await message.answer(
            text = text
        )
        
        delete_message_ids = [message_.message_id]
        await state.update_data(delete_message_ids = delete_message_ids)
        
        menu = await create_menu('main')
        await message.answer(text = menu['text'], reply_markup=menu['kb'])
        
        



       
@router.callback_query(HandlerCB.filter(F.action == 'delete_game_from_games_list'))
async def delete_game_from_games_list_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'service', 'games_list', 'delete_game_from_games_list'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.GAME} Выберите название игры')
    
    message_ = await callback.message.edit_text(
        text = text,
        reply_markup=SEARCH_INLINE_KB
    )

    await state.update_data(message_id = message_.message_id)
    await state.set_state(GamesListSG.delete_game_from_games_list_insert_game_state)
    
@router.message(GamesListSG.delete_game_from_games_list_insert_game_state)
async def delete_game_from_game_list_2_handler(message: Message, state: FSMContext):
    
    data = await state.get_data()
    message_id = data.get('message_id')
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    game =  message.text.strip()
    
    await message.delete()
    
    await delete_game_from_game_list(db, game)
     
    message_ = await message.answer(
        text = f'❌ Игра {game} удалена!'
    )
        
    delete_message_ids = [message_.message_id]
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])
    