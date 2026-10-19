from typing import Union

from app.core.dto.menu import MenuNode, MenuAction
from app.interfaces.bot.messages.menu import MenuTitle, ActionLabel
from .build_index import MenuBuildIndex


MENU_TREE = MenuNode(
    key='main',
    title=MenuTitle.MAIN,
    finance_fields=['revenue', 'on_account'],
    childrens=[
        # main-goods
        MenuNode(
            key='goods',
            title=MenuTitle.GOODS,
            childrens=[
                [
                    MenuAction(key='buy', title=ActionLabel.BUY, handler_action='buy-goods'),
                    MenuAction(key='sell', title=ActionLabel.SELL, handler_action='sell-goods')
                ],
                MenuAction(key='order_arrived', title=ActionLabel.ORDER_ARRIVED, handler_action='order-arrived'),
                MenuAction(key='change_selling_price', title=ActionLabel.CHANGE_SELLING_PRICE, handler_action='change-selling-price'),
                MenuAction(key='add_trns', title=ActionLabel.ADD_TRNS, handler_action='add-trns'),
                
                #main-goods
                MenuNode(
                    key='extra',
                    title=MenuTitle.EXTRA,
                    childrens=[
                        [
                            MenuAction(key='swap', title=ActionLabel.SWAP, handler_action='swap'),
                            MenuAction(key='reserve', title=ActionLabel.RESERVE, handler_action='reserve')
                        ],

                        MenuAction(key='comment', title=ActionLabel.COMMENT, handler_action='add-comment'),
                        
                        #main-goods-extra
                        MenuNode(
                            key='wrh_dlvr',
                            title=MenuTitle.WAREHOUSE_DELIVERY,
                            childrens=[
                                [
                                    MenuAction(key='to_me', title=ActionLabel.IN_TRANSIT_TO_ME, handler_action='goods_to_me'),
                                    MenuAction(key='to_client', title=ActionLabel.IN_TRANSIT_TO_CLIENT, handler_action='goods_to_client')
                                ],
                                
                                MenuAction(key='available_records', title=ActionLabel.AVAILABLE_RECORDS, handler_action='av-records'),
                                MenuAction(key='available_games', title=ActionLabel.AVAILABLE_GAMES, handler_action='av-games'),  
                                
                            ]
                        ),
                        # main-goods-extra-records_management
                        MenuNode(
                            key='management',
                            title=MenuTitle.RECORDS_MANAGEMENT,
                            childrens=[
                                MenuAction(key='cancel-order', title=ActionLabel.CANCEL_ORDER, handler_action='cancel-order'),
                                MenuAction(key='change_record', title=ActionLabel.CHANGE_ROW_BY_ID, handler_action='change_record'),
                                MenuAction(key='delete_record', title=ActionLabel.DELETE_ROW_BY_ID, handler_action='delete_record'),
                            ]
                        ),
                    ]
                ),
            ]
        ),
        
        # main-bulk_orders
        MenuNode(
            key='bulk_orders',
            title=MenuTitle.BULK_ORDERS,
            childrens=[
                MenuAction(key='create', title=ActionLabel.NEW_BULK_ORDER, handler_action='create_bulk_order'),
                MenuAction(key='add_delivery', title=ActionLabel.ADD_DELIVERY_TO_BULK_ORDER, handler_action='add_delivery_to_bulk_order'),
                MenuAction(key='arrived', title=ActionLabel.BULK_ORDER_ARRIVED, handler_action='bulk_order_arrived'),
                
                # main-bulk_orders-view_orders
                MenuNode(
                    key='view_orders',
                    title=MenuTitle.VIEW_ORDERS,
                    childrens=[
                        [
                            MenuAction(key='by_id', title=ActionLabel.ACTIVE_ORDERS, handler_action='active_orders'),
                            MenuAction(key='all', title=ActionLabel.ALL_BULK_ORDERS, handler_action='all_bulk_orders')
                        ],
                    ]
                ),
                
                # main-bulk_orders-management
                MenuNode(
                    key='management',
                    title=MenuTitle.MANAGEMENT,
                    childrens=[
                        MenuAction(key='delete', title=ActionLabel.DELETE_BULK_ORDER, handler_action='delete_bulk_order'),
                    ]
                ),
            ]
        ),
        
        # main-marketplaces
        MenuNode(
            key='marketplaces',
            title=MenuTitle.MARKETPLACES,
            childrens=[
                MenuNode(key='avito', title=MenuTitle.AVITO),
                MenuNode(key='ozon', title=MenuTitle.OZON),
            ]
        ),
        
        # main-extra
        MenuNode(
            key='extra',
            title=MenuTitle.EXTRA,
            childrens=[
                # main-extra-reports
                MenuNode(
                    key='reports',
                    title=MenuTitle.REPORTS,
                    childrens=[
                        MenuNode(
                            key='product',
                            title=MenuTitle.PRODUCT_REPORTS,
                            childrens=[
                                MenuAction(key='movement-report', title=ActionLabel.MOVEMENT_REPORT, handler_action='mov_report'),
                                MenuAction(key='sales-report', title=ActionLabel.SALES_REPORT, handler_action='sales_report'),
                            ]
                        ),
                        MenuAction(key='full_finance', title=ActionLabel.FULL_FINANCE_REPORT, handler_action='full_finance_report'),
                    ]
                ),
                
                # main-extra-games_catalog
                MenuNode(
                    key='games_catalog',
                    title=MenuTitle.GAMES_CATALOG,
                    childrens=[
                        MenuAction(key='add-game', title=ActionLabel.ADD_GAME, handler_action='add_game'),
                        MenuAction(key='update-game', title=ActionLabel.UPDATE_GAME, handler_action='update_game'),
                        MenuAction(key='delete', title=ActionLabel.DELETE_GAME, handler_action='delete_game'),
                    ]
                ),
                
                # main-extra-description
                MenuNode(
                    key='description',
                    title=MenuTitle.ANNOUNCEMENT_DESCRIPTION,
                    childrens=[
                        MenuAction(key='view', title=ActionLabel.VIEW_DESCRIPTION, handler_action='view_description'),
                        MenuAction(key='change', title=ActionLabel.CHANGE_PERSONAL_TAGS, handler_action='change_description'),
                    ]
                ),
            ]
        ),
    ],
)


MENU_INDEX: dict[str, Union[MenuNode, MenuAction]] = MenuBuildIndex.build_index(MENU_TREE)