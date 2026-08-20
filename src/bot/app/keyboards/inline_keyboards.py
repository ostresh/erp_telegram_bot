from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sys
import os
from aiogram.utils.keyboard import InlineKeyboardBuilder
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.bot.app.callbacks.callbacks import *
from src.bot.app.messages.menu_messages import MenuMessage
from src.bot.utils.utils import row_sizes



SEARCH_INLINE_KB = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔍 ПОИСК ИГРЫ",
                    switch_inline_query_current_chat="",
                )
            ],
            [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-records', title='back').pack()
        )],
        ]
    )


SEARCH_AV_INLINE_KB = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔍 ПОИСК ИГРЫ",
                    switch_inline_query_current_chat="@aviable ",
                )
            ],
            [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-records', title='back').pack()
        )],
        ]
    )


SEARCH_DELIVERY_TO_ME_INLINE_KB = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔍 ПОИСК ИГРЫ",
                    switch_inline_query_current_chat="@delivery_to_me ",
                )
            ],
            [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-records', title='back').pack()
        )],
        ]
    )


SEARCH_DELIVERY_TO_CLIENT_INLINE_KB = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔍 ПОИСК ИГРЫ",
                    switch_inline_query_current_chat="@delivery_to_client ",
                )
            ],
            [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-records', title='back').pack()
        )],
        ]
    )


SEARCH_RESERVE_INLINE_KB = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔍 ПОИСК ИГРЫ",
                    switch_inline_query_current_chat="@reserve ",
                )
            ],
            [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-records', title='back').pack()
        )],
        ]
    )


MAIN_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.RECORDS_TEXT,
            callback_data=MenuCB(path='main-records', title='records').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.INFO_TEXT,
            callback_data=MenuCB(path='main-info', title='info').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BULK_ORDER_TEXT,
            callback_data=MenuCB(path='main-bulk_order', title='bulk_order').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.NOTICE_TEXT,
            callback_data=MenuCB(path='main-notice', title='notice').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.TRNS_TEXT,
            callback_data=HandlerCB(action='add_trns_cb').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.SERVICE_TEXT,
            callback_data=MenuCB(path='main-service', title='service').pack()
        )],
    ],
)


MAIN_RECORDS_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=MenuMessage.BUY_TEXT,
                callback_data=HandlerCB(action='buy_disc').pack()
            ),
            InlineKeyboardButton(
                text=MenuMessage.SELL_TEXT,
                callback_data=HandlerCB(action='sell_disc').pack()
            )
        ],
        [InlineKeyboardButton(
            text=MenuMessage.ARRIVED_TEXT,
            callback_data=HandlerCB(action='order_arrived').pack()
        )],
        [
            InlineKeyboardButton(
                text=MenuMessage.SWAP_TEXT,
                callback_data=HandlerCB(action='swap_disc').pack()
            ),
            InlineKeyboardButton(
                text=MenuMessage.RESERVE_TEXT,
                callback_data=HandlerCB(action='reserve_disc').pack()
            )
        ],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-records', title='back').pack()
        )],
    ]
)


MAIN_INFO_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.RECORDS_TEXT,
            callback_data=MenuCB(path='main-info-records', title='records').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.AV_TEXT,
            callback_data=MenuCB(path='main-info-aviable', title='aviable').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BULK_ORDER_TEXT,
            callback_data=MenuCB(path='main-info-bulk_order', title='bulk_order').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.ALL_FINANCES_TEXT,
            callback_data=HandlerCB(action='get_all_finances').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-info', title='back').pack()
        )],
    ]
)


MAIN_BULK_ORDER_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.NEW_BULK_ORDER,
            callback_data=HandlerCB(action='new_bulk_order').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.ADD_DELIVERY_BULK_ORDER,
            callback_data=HandlerCB(action='add_delivery_to_bulk_order').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BULK_ORDER_ARRIVED_TEXT,
            callback_data=HandlerCB(action='bulk_order_arrived').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-bulk_order', title='back').pack()
        )],
    ]
)


MAIN_NOTICE_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
            text=MenuMessage.GENERAL_NOTICE_TEXT,
            callback_data=HandlerCB(action='general_notice').pack()),
            InlineKeyboardButton(
            text=MenuMessage.PERSONAL_NOTICE_TEXT,
            callback_data=HandlerCB(action='personal_notice').pack())
         ],
        [
            InlineKeyboardButton(
            text=MenuMessage.FOR_NEW_NOTICE_TEXT,
            callback_data=HandlerCB(action='for_new_notice').pack()),
            InlineKeyboardButton(
            text=MenuMessage.FOR_USED_NOTICE_TEXT,
            callback_data=HandlerCB(action='for_used_notice').pack())
        ],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-notice', title='back').pack()
        )],
    ]
)


MAIN_SERVICE_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.RECORDS_TEXT,
            callback_data=MenuCB(path='main-service-records', title='records').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.GAMES_LIST_TEXT,
            callback_data=MenuCB(path='main-service-games_list', title='games_list').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BULK_ORDER_TEXT,
            callback_data=MenuCB(path='main-service-bulk_order', title='bulk_order').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.NOTICE_TEXT,
            callback_data=MenuCB(path='main-service-notice', title='notice').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-service', title='back').pack()
        )],
    ]
)


MAIN_TRNS_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-trns', title='back').pack()
        )],
    ]
)


MAIN_INFO_RECORDS_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.COME_TO_ME_TEXT,
            callback_data=HandlerCB(action='delivery_to_me').pack()),
         InlineKeyboardButton(
            text=MenuMessage.COME_TO_CLIENT_TEXT,
            callback_data=HandlerCB(action='delivery_to_client').pack())
         ],
        [InlineKeyboardButton(
            text=MenuMessage.INTERVAL_TEXT,
            callback_data=HandlerCB(action='records_by_interval').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-info-records', title='back').pack()
        )],
    ]
)


MAIN_INFO_BULK_ORDER_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
            text=MenuMessage.INFO_BULK_ORDER_BY_ID_TEXT,
            callback_data=HandlerCB(action='one_bulk_order_by_id').pack()),
            InlineKeyboardButton(
            text=MenuMessage.COME_TO_ME_TEXT,
            callback_data=HandlerCB(action='bulk_orders_come_to_me').pack()),
         ],
        
        [InlineKeyboardButton(
            text=MenuMessage.ALL_BULK_ORDERS_TEXT,
            callback_data=HandlerCB(action='all_bulk_orders').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-info-bulk_order', title='back').pack()
        )],
    ]
)


MAIN_INFO_ALL_FINANCED_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-info-all_finances', title='back').pack()
        )],
    ]
)


MAIN_INFO_AV_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
            text=MenuMessage.AV_FOR_ME_TEXT,
            callback_data=HandlerCB(action='av_for_me').pack()),
            InlineKeyboardButton(
            text=MenuMessage.AV_FOR_CLIENT_TEXT,
            callback_data=HandlerCB(action='av_for_client').pack())
        ],
        [InlineKeyboardButton(
            text=MenuMessage.AV_BY_RECORDS_TEXT,
            callback_data=HandlerCB(action='av_by_records').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-info-aviable', title='back').pack()
        )],
    ]
)


MAIN_SERVICE_RECORDS_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.CHANGE_ROW_BY_ID_TEXT,
            callback_data=HandlerCB(action='change_row_by_id').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.UPDATE_PRICE_FOR_SPECIFIC_GAMES_TEXT,
            callback_data=HandlerCB(action='update_price_for_specific_games').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.DELETE_ROW_BY_ID_TEXT,
            callback_data=HandlerCB(action='delete_row_by_id').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-service-records', title='back').pack()
        )],
    ]
)


MAIN_SERVICE_NOTICE_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.CHANGE_PERSONAL_TAG_TEXT,
            callback_data=HandlerCB(action='change_personal_tags').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.CHANGE_BASE_FOR_NOTICE_TEXT,
            callback_data=HandlerCB(action='change_base_for_notice').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-service-notice', title='back').pack()
        )],
    ]
)


MAIN_SERVICE_GAMES_LIST_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.ADD_GAME_IN_GAMES_LIST_TEXT,
            callback_data=HandlerCB(action='add_game_to_games_list').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.DELETE_GAME_FROM_GAMES_LIST_TEXT,
            callback_data=HandlerCB(action='delete_game_from_games_list').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-service-games_list', title='back').pack()
        )],
    ]
)


MAIN_SERVICE_BULK_ORDER_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.DELETE_BULK_ORDER_BY_ID_TEXT,
            callback_data=HandlerCB(action='delete_bulk_order_by_id').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main-service-bulk_order', title='back').pack()
        )],
    ]
)


BACK_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main', title='back').pack()
        )],
    ]
)


LOCAL_OR_DELIVERY_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
            text=MenuMessage.LOCAL_TEXT,
            callback_data=HandlerCB(action='local').pack()),
            InlineKeyboardButton(
            text=MenuMessage.DELIVERY_TEXT,
            callback_data=HandlerCB(action='delivery').pack())
        ],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main', title='back').pack()
        )],
    ]
)


BASE_NOTICE_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text=MenuMessage.HEADER_NOTICE,
            callback_data=HandlerCB(action='header').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BASE_TAGS_NOTICE,
            callback_data=HandlerCB(action='base_tags').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BASE_PERSONAL,
            callback_data=HandlerCB(action='base_personal_tags').pack()
        )],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main', title='back').pack()
        )],
    ]
)


COME_TOME_OR_CLIENT_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
            text=MenuMessage.COME_TO_ME_TEXT,
            callback_data=HandlerCB(action='to_me').pack()),
            InlineKeyboardButton(
            text=MenuMessage.COME_TO_CLIENT_TEXT,
            callback_data=HandlerCB(action='to_client').pack())
        ],
        [InlineKeyboardButton(
            text=MenuMessage.BACK_TEXT,
            callback_data=MenuCB(path='main', title='back').pack()
        )],
    ]
)




async def inline_kb_factory(buttons, row_width):
    
    MAX_BUTTONS_IN_ROW = 4
    
    builder = InlineKeyboardBuilder()
    
    for item in buttons:
        builder.add(InlineKeyboardButton(text = item, callback_data=item))
    
    if row_width == 'equal':
        pattern = await row_sizes(len(buttons), MAX_BUTTONS_IN_ROW)
        
        builder.adjust(*pattern)
        
    else:
        
        builder.adjust(row_width)
    
    back_btn = InlineKeyboardButton(
        text='← Назад',
        callback_data=MenuCB(path='main', title='back').pack(),
    )
    
    builder.row(back_btn)
    
    return builder.as_markup()
