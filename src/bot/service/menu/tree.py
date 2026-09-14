from bot.service.menu.schemas import MenuNode, MenuAction
from bot.app.messages.menu import MenuTitle, ActionLabel

MENU_TREE = MenuNode(
    key='main', 
    title=MenuTitle.MAIN,
    finance_fields=['revenue', 'on_account'],
    children=[
        # main-records
        MenuNode(
            key='records', 
            title=MenuTitle.RECORDS,
            actions=[
                MenuAction(key='buy', title=ActionLabel.BUY, handler_action='buy'),
                MenuAction(key='sell', title=ActionLabel.SELL, handler_action='sell'),
                MenuAction(key='arrived', title=ActionLabel.ARRIVED, handler_action='order_arrived'),
                MenuAction(key='swap', title=ActionLabel.SWAP, handler_action='swap'),
                MenuAction(key='reserve', title=ActionLabel.RESERVE, handler_action='reserve'),
            ]
        ),
        
        # main-info
        MenuNode(
            key='info', 
            title=MenuTitle.INFO, 
            children=[
                # main-info-records
                MenuNode(
                    key='records', 
                    title=MenuTitle.RECORDS,
                    actions=[
                        MenuAction(key='come_to_me', title=ActionLabel.COME_TO_ME, handler_action='delivery_to_me'),
                        MenuAction(key='come_to_client', title=ActionLabel.COME_TO_CLIENT, handler_action='delivery_to_client'),
                        MenuAction(key='interval', title=ActionLabel.INTERVAL, handler_action='records_by_interval'),
                    ]
                ),
                
                # main-info-available
                MenuNode(
                    key='available', 
                    title=MenuTitle.AVAILABLE,
                    actions=[
                        MenuAction(key='for_me', title=ActionLabel.AVAILABLE_FOR_ME, handler_action='available_for_me'),
                        MenuAction(key='for_client', title=ActionLabel.AVAILABLE_FOR_CLIENT, handler_action='available_for_client'),
                        MenuAction(key='by_records', title=ActionLabel.AVAILABLE_BY_RECORDS, handler_action='available_by_records'),
                    ]
                ),
                
                # main-info-bulk_order
                MenuNode(
                    key='bulk_order', 
                    title=MenuTitle.BULK_ORDER,
                    actions=[
                        MenuAction(key='by_id', title=ActionLabel.BULK_ORDER_BY_ID, handler_action='bulk_order_by_id'),
                        MenuAction(key='come_to_me', title=ActionLabel.COME_TO_ME, handler_action='bulk_orders_come_to_me'),
                        MenuAction(key='all', title=ActionLabel.ALL_BULK_ORDERS, handler_action='all_bulk_orders'),
                    ]
                ),
                
                # main-info-all_finances
                MenuNode(
                    key='all_finances', 
                    title=ActionLabel.ALL_FINANCES
                ),
            ]
        ),
        
        # main-bulk_order
        MenuNode(
            key='bulk_order', 
            title=MenuTitle.BULK_ORDER,
            actions=[
                MenuAction(key='new', title=ActionLabel.NEW_BULK_ORDER, handler_action='new_bulk_order'),
                MenuAction(key='add_delivery', title=ActionLabel.ADD_DELIVERY_BULK_ORDER, handler_action='add_delivery_to_bulk_order'),
                MenuAction(key='arrived', title=ActionLabel.BULK_ORDER_ARRIVED, handler_action='bulk_order_arrived'),
            ]
        ),
        
        # main-notice
        MenuNode(
            key='notice', 
            title=MenuTitle.NOTICE,
            actions=[
                MenuAction(key='general', title=ActionLabel.GENERAL_NOTICE, handler_action='general_notice'),
                MenuAction(key='personal', title=ActionLabel.PERSONAL_NOTICE, handler_action='personal_notice'),
                MenuAction(key='for_new', title=ActionLabel.FOR_NEW_NOTICE, handler_action='for_new_notice'),
                MenuAction(key='for_used', title=ActionLabel.FOR_USED_NOTICE, handler_action='for_used_notice'),
            ]
        ),
        
        # main-trns
        MenuNode(
            key='trns', 
            title=MenuTitle.TRNS,
            actions=[
                MenuAction(key='add', title=ActionLabel.ADD_TRNS, handler_action='add_trns'),
            ]
        ),
        
        # main-service
        MenuNode(
            key='service', 
            title=MenuTitle.SERVICE, 
            children=[
                # main-service-records
                MenuNode(
                    key='records', 
                    title=MenuTitle.RECORDS,
                    actions=[
                        MenuAction(key='change_row', title=ActionLabel.CHANGE_ROW_BY_ID, handler_action='change_row_by_id'),
                        MenuAction(key='update_price', title=ActionLabel.UPDATE_PRICE_FOR_SPECIFIC_GAMES, handler_action='update_price_for_games'),
                        MenuAction(key='delete_row', title=ActionLabel.DELETE_ROW_BY_ID, handler_action='delete_row_by_id'),
                    ]
                ),
                
                # main-service-games_list
                MenuNode(
                    key='games_list', 
                    title=MenuTitle.GAMES_LIST,
                    actions=[
                        MenuAction(key='add', title=ActionLabel.ADD_GAME_IN_GAMES_LIST, handler_action='add_game'),
                        MenuAction(key='delete', title=ActionLabel.DELETE_GAME_FROM_GAMES_LIST, handler_action='delete_game'),
                    ]
                ),
                
                # main-service-bulk_order
                MenuNode(
                    key='bulk_order', 
                    title=MenuTitle.BULK_ORDER,
                    actions=[
                        MenuAction(key='delete', title=ActionLabel.DELETE_BULK_ORDER_BY_ID, handler_action='delete_bulk_order'),
                    ]
                ),
                
                # main-service-notice
                MenuNode(
                    key='notice', 
                    title=MenuTitle.NOTICE,
                    actions=[
                        MenuAction(key='change_personal_tag', title=ActionLabel.CHANGE_PERSONAL_TAG, handler_action='change_personal_tags'),
                        MenuAction(key='change_base', title=ActionLabel.CHANGE_BASE_FOR_NOTICE, handler_action='change_notice_base'),
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
    
    Автоматически заполняет для каждого узла:
    - path: полный путь (например, 'main-info-records')
    - parent_path: путь родителя (например, 'main-info')
    - crumbs: список заголовков для хлебных крошек
    
    Args:
        node: Текущий узел дерева
        parent_path: Путь родительского узла
        parent_crumbs: Хлебные крошки родителя
        
    Returns:
        Словарь {path: MenuNode} для всех узлов дерева
    """
    # Формируем путь текущего узла
    node.path = node.key if not parent_path else f'{parent_path}-{node.key}'
    
    # Сохраняем путь родителя
    node.parent_path = parent_path
    
    # Формируем хлебные крошки
    node.crumbs = (parent_crumbs or []) + [node.title]
    
    # Добавляем текущий узел в индекс
    index = {node.path: node}
    
    # Рекурсивно обрабатываем детей
    for child in node.children:
        index.update(build_index(child, node.path, node.crumbs))
    
    return index


MENU_INDEX: dict[str, MenuNode] = build_index(MENU_TREE)