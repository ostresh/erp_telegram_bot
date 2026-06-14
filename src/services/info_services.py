import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database import db
import asyncio
from utils.utils import get_trns_dict, get_games_dict
from utils.messages import create_block_of_messages_bulk_orders, create_blocks_of_messages_records, create_message_financial_indicators, change_message_group_games_by_prefixes
from utils.emoji import Emoji

async def get_info_of_financy(db, fields = None):
    
    id_trns_dict, trns_id_dict = await get_trns_dict(db)
    
    info_dict = {} 
    
    ALL_FIELDS = [
        "expences",
        "incomes",
        "revenue",
        "net_profit",
        "avito",
        "discs_count_sold",
        "avg_revenue",
        "on_account",
        "discs_count",
        "on_way",
        "on_way_count",
        "all_assets"
    ]
    
    if fields == ["__all__"] or fields == "__all__":
        fields = ALL_FIELDS.copy()
    
    
    # расходы
    if 'expences' in fields:
        expences = await db.fetch("SELECT * from records")
        expences = sum(list(map(lambda item: item.get('price_buy'), expences)))
        info_dict['expences'] = f"{expences:,}".replace(',', '.')
        
    # доходы
    if 'incomes' in fields:
        incomes = await db.fetch("SELECT price_sold from records where status = 'Нет' or status = 'Едет ко мне'")
        incomes = sum(list(map(lambda item: item.get('price_sold'), incomes)))
        info_dict['incomes'] = f"{incomes:,}".replace(',', '.')
    
    # выручка
    if 'revenue' in fields:
        revenue = await db.fetch("SELECT * FROM records WHERE game_id IS NOT NULL AND status = 'Нет' or status = 'Едет к покупателю'")
        revenue = map(lambda item: item.get('price_sold') - item.get('price_buy'), revenue)
        info_dict['revenue'] = f"{sum(list(revenue)):,}".replace(',', '.')
    
    # чистая прибыль
    if 'net_profit' in fields:
        # Получаем значения для расчета
        if 'incomes' not in fields:
            incomes = await db.fetch("SELECT price_sold from records where status = 'Нет' or status = 'Едет ко мне'")
            incomes = sum(list(map(lambda item: item.get('price_sold'), incomes)))
        else:
            incomes = int(info_dict['incomes'].replace('.', ''))
        
        if 'expences' not in fields:
            expences = await db.fetch("SELECT * from records")
            expences = sum(list(map(lambda item: item.get('price_buy'), expences)))
        else:
            expences = int(info_dict['expences'].replace('.', ''))
        
        info_dict['net_profit'] = f"{incomes - expences:,}".replace(',', '.')
    
    if 'avito' in fields:
        avito = await db.fetch(f"SELECT price_buy from records where trns_id = '{trns_id_dict.get('[TRNS] Авито')}'")
        avito = sum(list(map(lambda item: item.get('price_buy'), avito)))
        info_dict['avito'] = f"{avito:,}".replace(',', '.')
    
    # дисков продал
    if 'discs_count_sold' in fields:
        discs_count_sold = await db.fetch("SELECT COUNT(*) FROM records WHERE status='Нет' AND game_id IS NOT NULL AND trns_id IS NULL")
        info_dict['discs_count_sold'] = discs_count_sold[0].get('count')
    
    # средняя прибыль
    if 'avg_revenue' in fields:
        if 'revenue' not in fields:
            revenue = await db.fetch("SELECT * FROM records WHERE game_id IS NOT NULL AND status = 'Нет' or status = 'Едет к покупателю'")
            revenue = map(lambda item: item.get('price_sold') - item.get('price_buy'), revenue)
            revenue_value = f"{sum(list(revenue)):,}".replace(',', '.')
        else:
            revenue_value = info_dict['revenue']
        
        if 'discs_count_sold' not in fields:
            discs_count_sold = await db.fetch("SELECT COUNT(*) FROM records WHERE status='Нет' AND game_id IS NOT NULL AND trns_id IS NULL")
            discs_count_value = discs_count_sold[0].get('count')
        else:
            discs_count_value = info_dict['discs_count_sold']
        
        info_dict['avg_revenue'] = int(float(revenue_value.replace('.', '').replace(',', '.'))) // discs_count_value
    
    # на счету
    if 'on_account' in fields:
        if 'incomes' not in fields:
            incomes = await db.fetch("SELECT price_sold from records where status = 'Нет' or status = 'Едет ко мне'")
            incomes = sum(list(map(lambda item: item.get('price_sold'), incomes)))
        else:
            incomes = int(info_dict['incomes'].replace('.', ''))
        
        if 'expences' not in fields:
            expences = await db.fetch("SELECT * from records")
            expences = sum(list(map(lambda item: item.get('price_buy'), expences)))
        else:
            expences = int(info_dict['expences'].replace('.', ''))
        
        info_dict['on_account'] = f"{incomes - expences + 9403:,}".replace(',', '.')
    
    # дисков в наличии
    if 'discs_count' in fields:
        discs_count = await db.fetch("SELECT COUNT(*) from records where status = 'Да'")
        info_dict['discs_count'] = discs_count[0].get('count')
    
    # едет к покупателю
    if 'on_way' in fields or 'on_way_count' in fields:
        on_way = await db.fetch("SELECT price_sold from records where status = 'Едет к покупателю' and game_id is not null")
        on_way = list(map(lambda item: item.get('price_sold'), on_way))
        if 'on_way_count' in fields:
            info_dict['on_way_count'] = len(on_way)
        if 'on_way' in fields:
            info_dict['on_way'] = f'{sum(on_way):,}'.replace(',', '.')
        
    
    if 'all_assets' in fields:
        all_assets = 0
        
        if 'on_account' not in fields:
            if 'incomes' not in fields:
                incomes = await db.fetch("SELECT price_sold from records where status = 'Нет' or status = 'Едет ко мне'")
                incomes = sum(list(map(lambda item: item.get('price_sold'), incomes)))
            else:
                incomes = int(info_dict['incomes'].replace('.', ''))
            
            if 'expences' not in fields:
                expences = await db.fetch("SELECT * from records")
                expences = sum(list(map(lambda item: item.get('price_buy'), expences)))
            else:
                expences = int(info_dict['expences'].replace('.', ''))
            
            all_assets += incomes - expences + 9403
        
        else: all_assets += int(info_dict.get('on_account').replace('.', ''))
        
        
        if 'on_account' not in fields:
            on_way = await db.fetch("SELECT price_sold from records where status = 'Едет к покупателю' and game_id is not null")
            all_assets += sum(list(map(lambda item: item.get('price_sold'), on_way)))
        else:
            all_assets += int(info_dict.get('on_way').replace('.', ''))
            
        discs_av_cost = await db.fetch("SELECT price_buy, price_sell from records where status = 'Да'")
        discs_av_cost = sum([item.get('price_sell') if item.get('price_sell') else item.get('price_buy') for item in discs_av_cost])
        all_assets += discs_av_cost
        
        discs_av_cost_come_to_me = await db.fetch("SELECT price_buy, price_sell from records where status = 'Едет ко мне'")
        discs_av_cost_come_to_me = sum([item.get('price_sell') if item.get('price_sell') else item.get('price_buy') for item in discs_av_cost_come_to_me])
        all_assets += discs_av_cost_come_to_me
        
        info_dict['all_assets'] = f"{all_assets:,}".replace(',', '.')
        
    
    return await create_message_financial_indicators(db, info_dict)


    id_games_dict, games_id_dict = await get_games_dict(db)
    
    av_games_dict = {}
    av_games = await db.fetch("SELECT * from records where status = 'Да' and game_id is not null")
    av_games = list(map(lambda item: item.get('game_id'), av_games))
    av_games_unique = sorted(list(set(av_games)))
    
    result_ps4 = '\n🎯 <b>ИГРЫ ДЛЯ PS4:</b>\n'
    result_ps5 = '🎯 <b>ИГРЫ ДЛЯ PS5:</b>\n'
    result = ''
    
    for item in av_games_unique:
        av_games_dict[id_games_dict[item]] = av_games.count(item)
    
    for key, value in av_games_dict.items():
        if '[PS4]' in key:  
            result_ps4 += f'• <b>{key}</b> x{value}\n'.replace('[PS4] ', '')
        elif '[PS5]' in key:
            result_ps5 += f'• <b>{key}</b> x{value}\n'.replace('[PS5] ', '')
    result = result_ps5 + result_ps4
    return result.strip()

async def get_av_records_for_me(db):
    
    data = await db.fetch("SELECT records.game_id, games_list.name AS game_name, records.price_sell, MAX(records.price_buy) AS price_buy, COUNT(*) AS games_count FROM records JOIN games_list ON records.game_id = games_list.id WHERE records.status = 'Да' GROUP BY records.game_id, games_list.name, records.price_sell ORDER BY game_name ASC")
    
    ungroup_message = await create_blocks_of_messages_records(data, 15)
    
    return await change_message_group_games_by_prefixes(ungroup_message), data

async def get_av_records_for_client(db):
    
    data = await db.fetch("SELECT records.game_id, games_list.name AS game_name, records.price_sell FROM records JOIN games_list ON records.game_id = games_list.id WHERE records.status = 'Да' GROUP BY records.game_id, games_list.name, records.price_sell ORDER BY game_name ASC")
    
    blocks_messages = await create_blocks_of_messages_records(data, 15)
    
    ungroup_message = []
    
    for item in blocks_messages:
        item = item.replace(f"{Emoji.PRICE_BUY} 0р. ", '').replace(f" • {Emoji.PRICE_SOLD} 0р.", '')
        ungroup_message.append(item)
    
    return await change_message_group_games_by_prefixes(ungroup_message), data

async def get_records_delivery_to_me(db):
    
    data = await db.fetch("SELECT * from records where status = 'Едет ко мне' ORDER BY id ASC")

    return await create_blocks_of_messages_records(data, 10), data

async def get_records_delivery_to_client(db):
    
    data = await db.fetch("SELECT * from records where status = 'Едет к покупателю' ORDER BY id ASC")
    
    return await create_blocks_of_messages_records(data, 15), data
    
async def get_one_record_from_id(db, id):
    
    data = await db.fetch("SELECT * from records where id = $1", id)
    
    return await create_blocks_of_messages_records(data, 1), data

async def get_all_records_games(db):
    
    data = await db.fetch("SELECT * from records where game_id is not NULL ORDER BY id ASC")
    
    return await create_blocks_of_messages_records(data, 10), data

async def get_all_records_utils(db):
    
    data = await db.fetch("SELECT * from records where trns_id is not NULL ORDER BY id ASC")
    
    return await create_blocks_of_messages_records(data, 10), data

async def get_one_row_from_id(db, id):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    id_trns_dict, trns_id_dict = await get_trns_dict(db)
    
    data = await db.fetch("SELECT * from records where id = $1", id)
    
    data = data[0]
   
    result = f'''ID: {data.get('id')}
Дата покупки: {data.get('buy_at').strftime("%d.%m.%Y") if data.get('buy_at') else ''}
Дата продажи: {data.get('sold_at').strftime("%d.%m.%Y") if data.get('sold_at') else ''}
Игра: {id_games_dict[data.get('game_id')] if data.get('game_id') else ''}
Транзакция: {id_trns_dict[data.get('trns_id')] if data.get('trns_id') else ''}
Цена покупки: {data.get('price_buy') if data.get('price_buy') else 0}
Цена продажи: {data.get('price_sell') if data.get('price_sell') else 0}
Цена продано: {data.get('price_sold') if data.get('price_sold') else 0}
Статус: {data.get('status') if data.get('status') else ''}
Обмен: {data.get('swap') if data.get('swap') else ''}
Бронь: {data.get('reserve') if data.get('reserve') else ''}
Комментарий: {data.get('comment') if data.get('comment') else ''}'''

    return result         

async def get_one_bulk_order_from_id(db, id):
    
    data = await db.fetch('SELECT * from bulk_orders where id = $1 ORDER BY id ASC', id)
    
    return await create_block_of_messages_bulk_orders(data, 1), data

async def get_all_bulk_orders(db):
    
    data = await db.fetch('SELECT * from bulk_orders ORDER BY id ASC')
    
    return await create_block_of_messages_bulk_orders(data, 10), data

async def get_bulk_orders_delivery_to_me(db):
    
    data = await db.fetch("SELECT * from bulk_orders WHERE order_status = 'Едет ко мне' ORDER BY id ASC")
    
    return await create_block_of_messages_bulk_orders(data, 10), data

async def get_records_from_bulk_order_from_id(db, id):

    interval_records_id = await db.fetch('SELECT interval_records_id from bulk_orders WHERE id = $1', id)
    interval_records_id = interval_records_id[0].get('interval_records_id')
    interval_bottom = int(interval_records_id.split('-')[0])
    interval_top = int(interval_records_id.split('-')[1])
    
    data = await db.fetch('SELECT * FROM records where id BETWEEN $1 and $2', interval_bottom, interval_top)
    
    return await create_blocks_of_messages_records(data, 10), data   

async def get_specific_games_in_aviable(db, game):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    
    data = await db.fetch("SELECT * FROM records where game_id = $1 and status = 'Да'", games_id_dict[game])
    
    return await create_blocks_of_messages_records(data, 10), data

async def get_specific_games_delivery_to_me_without_bulk_order(db, game):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    
    data = await db.fetch("SELECT * FROM records where game_id = $1 and status = 'Едет ко мне' AND COALESCE(comment, '') NOT ILIKE '%Оптовый заказ%' ORDER by ID", games_id_dict[game])
    
    return await create_blocks_of_messages_records(data, 10), data

async def get_specific_games_for_reserve(db, game):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    
    data = await db.fetch(f"SELECT * FROM records WHERE game_id = $1 AND (status = 'Едет ко мне' OR status = 'Да') AND reserve IS NULL ORDER BY id", games_id_dict[game])
    
    return await create_blocks_of_messages_records(data, 10), data

async def get_specific_games_delivery_to_client(db, game):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    
    data = await db.fetch("SELECT * FROM records where game_id = $1 and status = 'Едет к покупателю' ORDER by ID", games_id_dict[game])
    
    return await create_blocks_of_messages_records(data, 10), data

async def get_records_from_interval_id(db, interval_id):
    
    interval_bottom = int(interval_id.split('-')[0])
    interval_top = int(interval_id.split('-')[1])
    
    data = await db.fetch('SELECT * FROM records where id BETWEEN $1 and $2', interval_bottom, interval_top)
    
    return await create_blocks_of_messages_records(data, 10), data

async def get_av_records(db):
    
    data = await db.fetch("SELECT * FROM records where status = 'Да' ORDER BY id ASC")
    
    return await create_blocks_of_messages_records(data, 10), data


async def main():
    try:
        await db.connect()
        
        print(await get_info_of_financy(db, ['all_assets']))
        
    except Exception as e:
        print(e)
    finally:
        await db.close()
    
if __name__=='__main__':
    asyncio.run(main())