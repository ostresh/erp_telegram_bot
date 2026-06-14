from aiogram import Router,F
from aiogram.types import Message
import sys
from aiogram import Router,F
from aiogram.types import Message, CallbackQuery
import sys
import os
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database import Database, db
import asyncio
from states.states import NoticeSG
from services.notices_services import *
# from services.info_services import *
from keyboards.inline_keyboards import *
from services.menu_services import create_menu_text, create_menu
from utils.emoji import Emoji
from states.states import NoticeSG

router = Router()


@router.callback_query(HandlerCB.filter(F.action == 'general_notice'))
async def general_notice_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    general_notice = await create_general(db)
    
    await callback.message.delete()
    
    delete_message_ids = []
    
    general_notice_messages = [await callback.message.answer(item, parse_mode=None) for item in general_notice]
    delete_message_ids += list(map(lambda item: item.message_id, general_notice_messages))
    
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])
    
@router.callback_query(HandlerCB.filter(F.action == 'for_new_notice'))
async def for_new_notice_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    general_notice = await create_for_new(db)
    
    await callback.message.delete()
    
    delete_message_ids = []
    
    general_notice_messages = [await callback.message.answer(item, parse_mode=None) for item in general_notice]
    delete_message_ids += list(map(lambda item: item.message_id, general_notice_messages))
    
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])
    
@router.callback_query(HandlerCB.filter(F.action == 'for_used_notice'))
async def for_used_notice_main_handler(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    general_notice = await create_for_used(db)
    
    await callback.message.delete()
    
    delete_message_ids = []
    
    general_notice_messages = [await callback.message.answer(item, parse_mode=None) for item in general_notice]
    delete_message_ids += list(map(lambda item: item.message_id, general_notice_messages))
    
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await callback.message.answer(text = menu['text'], reply_markup=menu['kb'])



@router.callback_query(HandlerCB.filter(F.action == 'personal_notice'))
async def personal_notice_main_hanlder(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'notice', 'personal_notice'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.GAME} Введите название игры')
    
    await callback.message.edit_text(
        text = text,
        reply_markup=SEARCH_INLINE_KB
    )
    
    message_id = callback.message.message_id
    
    await state.set_state(NoticeSG.personal_notice_insert_game_state)
    await state.update_data(message_id = message_id)

@router.message(StateFilter(NoticeSG.personal_notice_insert_game_state))
async def personal_notice_2_hanlder(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    
    game = message.text.strip()
    
    await message.delete()
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    personal_notice = await create_personal(db, game)
    
    personal_notice_message = await message.answer(personal_notice, parse_mode=None)
    
    delete_message_ids = [personal_notice_message.message_id]
    
    await state.update_data(delete_message_ids=delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])



@router.callback_query(HandlerCB.filter(F.action == 'change_base_for_notice'))
async def change_base_for_notice_main_hanlder(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):

    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'service', 'notice', 'change_base_for_notice'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.TAGS} Выберите элемент для изменения')
    
    message_ = await callback.message.edit_text(
        text = text,
        reply_markup=BASE_NOTICE_INLINE_KB
    )
    
    await state.set_state(NoticeSG.change_base_select_base_state)

@router.callback_query(HandlerCB.filter(), StateFilter(NoticeSG.change_base_select_base_state))
async def change_base_for_notice_2_hanlder(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    await callback.answer(show_alert=False)
    
    base = callback_data.action
    await state.update_data(base = base)
    await callback.message.delete()
    
    base_message = await callback.message.answer(
        text = await get_base_for_notice(db, base),
        parse_mode=None
    )
    
    message_ = await callback.message.answer(
        text = "⤵️ Введите новое описание",
    )
    
    delete_message_ids = [message_.message_id, base_message.message_id]
    await state.set_state(NoticeSG.change_base_insert_new_base_state)
    await state.update_data(delete_message_ids = delete_message_ids)

@router.message(StateFilter(NoticeSG.change_base_insert_new_base_state))
async def change_base_for_notice_3_hanlder(message: Message, state: FSMContext):
    
    data = await state.get_data()
    delete_message_ids = data.get('delete_message_ids')
    base = data.get('base')
    
    new_title = message.text.strip()
    
    await message.delete()
    await message.bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=delete_message_ids
    )
    
    await change_base_for_description(db, base, new_title)
    
    new_title = await get_base_for_notice(db, base)
    
    text = f"""
{Emoji.TAGS} <b>ТИП</b>: {base}

{new_title}
"""
    
    base_message = await message.answer(
        text = text,
        parse_mode="HTML"
    )
    
    delete_message_ids.append(base_message.message_id)
    await state.update_data(delete_message_ids = delete_message_ids)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])
    
    
    
    
@router.callback_query(HandlerCB.filter(F.action == 'change_personal_tags'))
async def change_personal_tags_main_hanlder(callback: CallbackQuery, callback_data: HandlerCB, state: FSMContext):
    
    await callback.answer(show_alert=False)
    
    text = await create_menu_text(['main', 'service', 'notice', 'change_personal_tags'])
    
    text = text.replace(MenuMessage.ADDON_TEXT, f'{Emoji.GAME} Введите название игры')
    
    await callback.message.edit_text(
        text = text,
        reply_markup=SEARCH_INLINE_KB
    )
    
    message_id = callback.message.message_id
    
    await state.set_state(NoticeSG.change_personal_tags_insert_game_state)
    await state.update_data(message_id = message_id)

@router.message(StateFilter(NoticeSG.change_personal_tags_insert_game_state))
async def change_personal_tags_2_hanlder(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    
    game = message.text.strip()
    await state.update_data(game = game)
    
    await message.delete()
    
    await message.bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    
    base_message = await message.answer(
        text = await get_personal_tag(db, game),
        parse_mode=None
    )
    
    message_ = await message.answer(
        text = "⤵️ Введите новое описание",
    )
    
    delete_message_ids = [message_.message_id, base_message.message_id]
    
    await state.update_data(delete_message_ids=delete_message_ids)
    await state.set_state(NoticeSG.change_personal_tags_insert_new_tags_state)
    
@router.message(StateFilter(NoticeSG.change_personal_tags_insert_new_tags_state))
async def change_personal_tags_3_hanlder(message: Message, state: FSMContext):
    data = await state.get_data()
    delete_message_ids = data.get('delete_message_ids')
    game = data.get('game')
    
    new_tags = message.text.strip()
    
    await message.delete()
    
    await message.bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=delete_message_ids
    )
    
    await change_personal_tag(db, game, new_tags)
    
    personal_tag = await get_personal_tag(db, game)
    
    text = f"""
{Emoji.GAME} <b>ИГРА</b>: {game}

{personal_tag}
"""
    
    personal_tag_message = await message.answer(text, parse_mode="HTML")
    
    delete_message_ids = [personal_tag_message.message_id]
    
    await state.update_data(delete_message_ids=delete_message_ids)
    await state.set_state(NoticeSG.change_personal_tags_insert_new_tags_state)
    
    menu = await create_menu('main')
    await message.answer(text = menu['text'], reply_markup=menu['kb'])