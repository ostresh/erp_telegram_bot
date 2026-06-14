
from bot.messages.menu_messages import MenuMessage
from services.info_services import get_info_of_financy
from database import Database, db
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from bot.keyboards.inline_keyboards import *

async def create_menu_text(fields = None):
    
    messages_dict={
    "main": MenuMessage.MAIN_TEXT,
    "records": MenuMessage.RECORDS_TEXT,
    "info": MenuMessage.INFO_TEXT,
    "bulk_order": MenuMessage.BULK_ORDER_TEXT,
    "notice": MenuMessage.NOTICE_TEXT,
    "service": MenuMessage.SERVICE_TEXT,
    "av": MenuMessage.AV_TEXT,
    "all_finances": MenuMessage.ALL_FINANCES_TEXT,
    "games_list": MenuMessage.GAMES_LIST_TEXT,
    "notice" : MenuMessage.NOTICE_TEXT,
    "trns" : MenuMessage.TRNS_TEXT,
    "buy_discs": MenuMessage.BUY_TEXT,
    "sell_discs" : MenuMessage.SELL_TEXT,
    "order_arrived" : MenuMessage.ARRIVED_TEXT,
    "swap": MenuMessage.SWAP_TEXT,
    "come_to_me": MenuMessage.COME_TO_ME_TEXT,
    "come_to_client": MenuMessage.COME_TO_CLIENT_TEXT,
    "records_by_interval": MenuMessage.INTERVAL_TEXT,
    "one_bulk_order_by_id": MenuMessage.INFO_BULK_ORDER_BY_ID_TEXT,
    "new_bulk_order": MenuMessage.NEW_BULK_ORDER,
    "add_delivery_to_bulk_order": MenuMessage.ADD_DELIVERY_BULK_ORDER,
    "personal_notice" : MenuMessage.PERSONAL_NOTICE_TEXT,
    "change_row_by_id" : MenuMessage.CHANGE_ROW_BY_ID_TEXT,
    "update_price_for_specific_games" : MenuMessage.UPDATE_PRICE_FOR_SPECIFIC_GAMES_TEXT,
    "delete_row_by_id" : MenuMessage.DELETE_ROW_BY_ID_TEXT,
    "add_game_to_games_list" : MenuMessage.ADD_GAME_IN_GAMES_LIST_TEXT,
    "delete_game_from_games_list" : MenuMessage.DELETE_GAME_FROM_GAMES_LIST_TEXT,
    "delete_bulk_order_by_id" : MenuMessage.DELETE_BULK_ORDER_BY_ID_TEXT,
    "change_base_for_notice" : MenuMessage.CHANGE_BASE_FOR_NOTICE_TEXT,
    "change_personal_tags" : MenuMessage.CHANGE_PERSONAL_TAG_TEXT,
    "reserve" : MenuMessage.RESERVE_TEXT,
    
}
    
    message = []
    
    if fields == ['main']:
        financy = await get_info_of_financy(db, ['revenue', 'on_account'])
        message.append(financy.replace('\n\n', '\n') + '\n')
    
    for i in range(len(fields)):
        if i == 0:
            message.append(f'<b>{messages_dict.get(fields[i])}</b>\n')
        else:
            message.append(f'→<b>{messages_dict.get(fields[i])}</b>\n')
    
    
    return "".join(message) + '\n' + MenuMessage.ADDON_TEXT

async def back_menu(path):
    BACK_DICT = {
    ('main'): {
        'text': await create_menu_text(['main']),
        'kb' : MAIN_INLINE_KB
    },
    
    ('main-records', 'main-info', 'main-bulk_order', 'main-notice', 'main-service', 'main-trns'): {
        'text': await create_menu_text(['main']),
        'kb' : MAIN_INLINE_KB
    },
    
    ('main-info-records', 'main-info-bulk_order', 'main-info-all_finances', 'main-info-aviable'): {
        'text': await create_menu_text(['main', 'info']),
        'kb' : MAIN_INFO_INLINE_KB
    },
    
    ('main-service-records', 'main-service-notice', 'main-service-games_list', 'main-service-bulk_order'): {
        'text': await create_menu_text(['main', 'service']),
        'kb' : MAIN_SERVICE_INLINE_KB
    },
    
    
    
    }
    
    for key in BACK_DICT.keys():
        if path in key:
            return {'text': BACK_DICT[key]['text'], 'kb' : BACK_DICT[key]['kb']}

async def create_menu(path):
    
    MENU_DICT = {
        
        # Главное меню
        'main': {
            'text': await create_menu_text(['main']),
            'kb': MAIN_INLINE_KB
        },
        
        # Кнопки Главная
        'main-records': {
            'text': await create_menu_text(['main', 'records']),
            'kb': MAIN_RECORDS_INLINE_KB
        },
        'main-info': {
            'text': await create_menu_text(['main', 'info']),
            'kb': MAIN_INFO_INLINE_KB
        },
        'main-bulk_order': {
            'text': await create_menu_text(['main', 'bulk_order']),
            'kb': MAIN_BULK_ORDER_INLINE_KB
        },
        'main-service': {
            'text': await create_menu_text(['main', 'service']),
            'kb': MAIN_SERVICE_INLINE_KB
        },
        'main-trns': {
            'text': await create_menu_text(['main', 'trns']),
            'kb': MAIN_TRNS_INLINE_KB
        },
        'main-notice': {
            'text': await create_menu_text(['main', 'notice']),
            'kb': MAIN_NOTICE_INLINE_KB
        },
        
        # Кнопки Главная → Меню Информации
        'main-info-records': {
            'text': await create_menu_text(['main', 'info', 'records']),
            'kb': MAIN_INFO_RECORDS_INLINE_KB
        },
        'main-info-bulk_order': {
            'text': await create_menu_text(['main', 'info', 'bulk_order']),
            'kb': MAIN_INFO_BULK_ORDER_INLINE_KB
        },
        'main-info-aviable': {
            'text': await create_menu_text(['main', 'info', 'av']),
            'kb': MAIN_INFO_AV_INLINE_KB
        },
        
        # Кнопки Главная → Меню Сервиса
        'main-service-records': {
            'text': await create_menu_text(['main', 'service', 'records']),
            'kb': MAIN_SERVICE_RECORDS_INLINE_KB
        },
        'main-service-games_list': {
            'text': await create_menu_text(['main', 'service', 'games_list']),
            'kb': MAIN_SERVICE_GAMES_LIST_INLINE_KB
        },
        'main-service-bulk_order': {
            'text': await create_menu_text(['main', 'service', 'bulk_order']),
            'kb': MAIN_SERVICE_BULK_ORDER_INLINE_KB
        },
        'main-service-notice': {
            'text': await create_menu_text(['main', 'service', 'notice']),
            'kb': MAIN_SERVICE_NOTICE_INLINE_KB
        },
    }
    
    return {'text': MENU_DICT[path]['text'], 'kb': MENU_DICT[path]['kb']}