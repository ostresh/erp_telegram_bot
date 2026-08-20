from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    personal_notice_state = State()
    change_personal_tag_state = State()
    change_base_for_description_state = State()
    buy_state = State()
    change_status_state = State()
    sell_state = State()
    swap_state = State()
    reserve_state = State()
    order_arrived_state = State()
    update_one_row_state = State()
    delete_row_state = State()
    add_game_in_game_list_state = State()
    delete_game_from_game_list_state = State()
    add_bulk_order_state = State()
    add_delivery_to_bulk_order_from_id_state = State()
    bulk_order_arrived_from_id_state = State()
    get_one_bulk_order_state = State()
    delete_bulk_order_from_id_state = State()
    get_records_from_bulk_order_from_id_state = State()
    update_price_sell_for_specific_games_state = State()
    get_records_from_interval_id_state = State()
    trns_state = State()
    
class RecordsSG(StatesGroup):
    
    trns_insert_trns_state = State()
    trns_insert_price_and_comment_state = State()
    answer_trns = State()
    
    buy_insert_game_state = State()
    buy_insert_get_type_state = State()
    buy_insert_data_state = State()
    
    sell_select_records_id_state = State()
    sell_select_records_id_cb_state = State()
    sell_insert_prices_state = State()
    sell_insert_data_state = State()
    
    order_arrived_insert_game_state = State()
    order_arrived_output_records_state = State()
    order_arrived_insert_data_state = State()
    
    swap_insert_ids_state = State()
    
    reserve_insert_game_state = State()
    reserve_select_id_state = State()
    reserve_insert_name_state = State()
    
    change_row_by_id_insert_id_state = State()
    change_row_by_id_insert_new_row_state = State()
    
    update_price_for_specific_games_insert_game_state = State()
    update_price_for_specific_games_insert_price_sell_state = State()
    
    delete_row_by_id_insert_id_state = State()
    

class InfoSG(StatesGroup):
    
    interval_insert_interval_state = State()
    
    bulk_orders_output_state = State()

  
class BulkOrderSG(StatesGroup):
    
    new_bulk_order_insert_csv_state = State()
    
    add_delivery_to_bulk_order_select_id_state = State()
    add_delivery_to_bulk_order_insert_price_state = State()
    
    bulk_order_come_to_me_state = State()
    
    delete_bulk_order_insert_id_state = State()
    
    
class NoticeSG(StatesGroup):
    
    personal_notice_insert_game_state = State()
    
    change_base_select_base_state = State()
    change_base_insert_new_base_state = State()
    
    change_personal_tags_insert_game_state = State()
    change_personal_tags_insert_new_tags_state = State()
    

class GamesListSG(StatesGroup):
    
    add_game_to_games_list_insert_name_state = State()
    add_game_to_games_list_insert_tags_state = State()
    
    delete_game_from_games_list_insert_game_state = State()