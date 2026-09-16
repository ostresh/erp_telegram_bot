from app.service.menu.schemas import MenuNode, MenuAction
from app.bot.messages.menu import MenuTitle, ActionLabel


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
                    MenuAction(key='buy', title=ActionLabel.BUY, handler_action='buy'),
                    MenuAction(key='sell', title=ActionLabel.SELL, handler_action='sell')
                ],
                MenuAction(key='order_arrived', title=ActionLabel.ORDER_ARRIVED, handler_action='order_arrived'),
                [
                    MenuAction(key='swap', title=ActionLabel.SWAP, handler_action='swap'),
                    MenuAction(key='reserve', title=ActionLabel.RESERVE, handler_action='reserve')
                ],
                MenuAction(key='change_selling_price', title=ActionLabel.CHANGE_SELLING_PRICE, handler_action='change_selling_price'),
                MenuAction(key='add_trns', title=ActionLabel.ADD_TRNS, handler_action='add_trns'),
                
                # main-goods-warehouse_delivery
                MenuNode(
                    key='warehouse_delivery',
                    title=MenuTitle.WAREHOUSE_DELIVERY,
                    childrens=[
                        [
                            MenuAction(key='delivery_to_me', title=ActionLabel.DELIVERY_TO_ME, handler_action='delivery_to_me'),
                            MenuAction(key='delivery_to_client', title=ActionLabel.DELIVERY_TO_CLIENT, handler_action='delivery_to_client')
                        ],
                        MenuAction(key='available', title=ActionLabel.AVAILABLE, handler_action='available'),
                    ]
                ),
                
                # main-goods-records_management
                MenuNode(
                    key='records_management',
                    title=MenuTitle.RECORDS_MANAGEMENT,
                    childrens=[
                        MenuAction(key='change_row', title=ActionLabel.CHANGE_ROW_BY_ID, handler_action='change_row_by_id'),
                        MenuAction(key='delete_row', title=ActionLabel.DELETE_ROW_BY_ID, handler_action='delete_row_by_id'),
                    ]
                ),
            ]
        ),
        
        # main-bulk_orders
        MenuNode(
            key='bulk_orders',
            title=MenuTitle.BULK_ORDERS,
            childrens=[
                MenuAction(key='new', title=ActionLabel.NEW_BULK_ORDER, handler_action='new_bulk_order'),
                MenuAction(key='add_delivery', title=ActionLabel.ADD_DELIVERY_TO_BULK_ORDER, handler_action='add_delivery_to_bulk_order'),
                MenuAction(key='arrived', title=ActionLabel.BULK_ORDER_ARRIVED, handler_action='bulk_order_arrived'),
                
                # main-bulk_orders-view_orders
                MenuNode(
                    key='view_orders',
                    title=MenuTitle.VIEW_ORDERS,
                    childrens=[
                        MenuAction(key='come_to_me', title=ActionLabel.BULK_ORDERS_COME_TO_ME, handler_action='bulk_orders_come_to_me'),
                        [
                            MenuAction(key='by_id', title=ActionLabel.BULK_ORDER_BY_ID, handler_action='bulk_order_by_id'),
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
                        MenuAction(key='full_finance', title=ActionLabel.FULL_FINANCE_REPORT, handler_action='full_finance_report'),
                        MenuAction(key='product_period', title=ActionLabel.PRODUCT_REPORT_PERIOD, handler_action='product_report_period'),
                    ]
                ),
                
                # main-extra-games_catalog
                MenuNode(
                    key='games_catalog',
                    title=MenuTitle.GAMES_CATALOG,
                    childrens=[
                        MenuAction(key='add', title=ActionLabel.ADD_GAME, handler_action='add_game'),
                        MenuAction(key='delete', title=ActionLabel.DELETE_GAME, handler_action='delete_game'),
                    ]
                ),
                
                # main-extra-description
                MenuNode(
                    key='description',
                    title=MenuTitle.ANNOUNCEMENT_DESCRIPTION,
                    childrens=[
                        MenuAction(key='view', title=ActionLabel.VIEW_DESCRIPTION, handler_action='view_description'),
                        MenuAction(key='change', title=ActionLabel.CHANGE_PERSONAL_TAGS, handler_action='change_personal_tags'),
                    ]
                ),
            ]
        ),
    ],
)


def build_index(
    node: MenuNode,
    parent_path: str | None = None,
    parent_crumbs: list[str] | None = None,
) -> dict[str, MenuNode]:
    """
    Рекурсивно обходит дерево и собирает индекс.
    
    Обрабатывает только MenuNode (MenuAction пропускаются, так как они не имеют детей).
    
    Args:
        node: Текущий узел дерева
        parent_path: Путь родительского узла
        parent_crumbs: Хлебные крошки родителя
        
    Returns:
        Словарь {path: MenuNode} для всех узлов дерева
    """
    node.path = node.key if not parent_path else f'{parent_path}-{node.key}'
    node.parent_path = parent_path
    node.crumbs = (parent_crumbs or []) + [node.title]
    
    index = {node.path: node}
    
    for child in node.childrens:
        if isinstance(child, MenuNode):
            index.update(build_index(child, node.path, node.crumbs))
    
    return index


MENU_INDEX: dict[str, MenuNode] = build_index(MENU_TREE)