import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database import db
import asyncio
from utils.utils import get_games_dict, get_today
from datetime import datetime, timezone, timedelta
import csv
from io import StringIO
from .records_services import add_records

async def add_bulk_order(db, **kwargs):
    
    columns = ", ".join(list(kwargs.keys()))
    
    placeholders = ", ".join(f"${i+1}" for i in range(len(kwargs)))
    
    values = list(kwargs.values())
    
    sql = f'INSERT INTO bulk_orders ({columns}) VALUES ({placeholders})'
    
    await db.execute(sql, *values) 

async def new_bulk_order(db, csv_string):

    data = list(csv.DictReader(StringIO(csv_string), ["game", 'price_buy', 'total_count', "seller", "reserve", "prepay"],delimiter=';'))
    
    last_id_in_records = await db.fetch('SELECT id from records ORDER BY id DESC LIMIT 1')
    last_id_in_records = last_id_in_records[0].get('id')
    
    last_id_in_bulk_order = await db.fetch('SELECT id from bulk_orders ORDER BY id DESC LIMIT 1')
    last_id_in_bulk_order = last_id_in_bulk_order[0].get('id')
    
    interval_records_id = ''
    total_count = 0
    total_cost = 0
    
    for item in data:
        total_count += int(item.get('total_count'))
        total_cost += int(item.get('total_count')) * int(item.get('price_buy'))
        interval_records_id = f'{last_id_in_records+1}-{last_id_in_records+total_count}'
    
    data_bulk_order = {
        'id': last_id_in_bulk_order + 1,
        'created_at': await get_today(),
        'interval_records_id': interval_records_id,
        'seller' : data[0].get('seller'),
        'order_status' : "Едет ко мне",
        'total_count' : total_count,
        'total_cost' : total_cost,
    }
        
    await add_bulk_order(db, **data_bulk_order)
    
    id_ = last_id_in_records + 1
    
    for item in data:
        reserve_list = item.get('reserve').split(',')
        prepay_list = item.get('prepay').split(',')
        for _ in range(int(item.get('total_count'))):
            try:
                reserve = reserve_list[_].strip()
            except:
                reserve = None
                
            try:
                prepay = prepay_list[_].strip()
            except:
                prepay = 0
            
            data_db = {
                'id' : int(id_),
                'buy_at': await get_today(),
                'game_id' : item.get('game'),
                'price_buy' : int(item.get('price_buy')),
                'price_sell' : 0,
                'price_sold': int(prepay) if prepay != '' else 0,
                'status' : 'Едет ко мне',
                'reserve' : reserve if reserve != '' else None,
                'comment' : f"Оптовый заказ №{data_bulk_order.get('id')}"
            }
            
            await add_records(db, **data_db)
            
            id_ += 1
              
    return data_bulk_order.get('id')

async def add_delivery_to_bulk_order_from_id(db, id, delivery_cost):

    data = await db.fetch('SELECT * FROM bulk_orders WHERE id = $1', id)
    total_count = data[0].get('total_count')
    interval_records_id = data[0].get('interval_records_id')
    
    delivery_cost_for_one_disc = delivery_cost // total_count
    remains_delivery_cost = delivery_cost - (delivery_cost_for_one_disc*total_count)
    interval_bottom = int(interval_records_id.split('-')[0])
    interval_top = int(interval_records_id.split('-')[1])
    
    await db.execute("UPDATE bulk_orders SET delivery_cost = $2 WHERE id = $1", id, delivery_cost)
    
    for i in range(interval_bottom, interval_top+1):
        if remains_delivery_cost > 0:
            
            data_db = {
                'id' : i,
                'price_buy' : int(delivery_cost_for_one_disc) + 1
            }
            remains_delivery_cost -= 1
        else:
            data_db = {
                'id' : i,
                'price_buy' : int(delivery_cost_for_one_disc)
            }
        await db.execute("UPDATE records SET price_buy = price_buy + $2 WHERE id = $1;", data_db.get('id'), data_db.get('price_buy'))   
            
async def delete_bulk_order_from_id(db, id):
    interval_records_id = await db.fetch('SELECT interval_records_id from bulk_orders WHERE id = $1', id)
    interval_records_id = interval_records_id[0].get('interval_records_id')
    interval_bottom = int(interval_records_id.split('-')[0])
    interval_top = int(interval_records_id.split('-')[1])
    await db.execute('DELETE FROM bulk_orders WHERE id = $1', id)
    await db.execute('DELETE FROM records WHERE id BETWEEN $1 AND $2', interval_bottom, interval_top)
    
async def bulk_order_arrived_from_id(db, id):
    interval_records_id = await db.fetch('SELECT interval_records_id from bulk_orders WHERE id = $1', id)
    interval_records_id = interval_records_id[0].get('interval_records_id')
    interval_bottom = int(interval_records_id.split('-')[0])
    interval_top = int(interval_records_id.split('-')[1])
    await db.execute("UPDATE bulk_orders SET order_status = 'Завершен', arrived_at = $2 WHERE id = $1", id, datetime.now(timezone(timedelta(hours=5))).date())
    await db.execute("UPDATE records SET status = 'Да' WHERE id BETWEEN $1 AND $2", interval_bottom, interval_top)

async def check_bulk_order_by_id(db, id):
    
    check = await db.fetch("SELECT * FROM bulk_orders where id = $1", id)

    if len(check) == 0: return False
    else: return True

async def change_records_comments_from_bulk_orders(db):
    
    data_bulk_orders = await db.fetch("SELECT * from bulk_orders ORDER by id")
    
    intervals = []
    
    for item in data_bulk_orders:
        dict_ = {}
        id_order_bulk = item.get('id')
        interval_records_id = item.get('interval_records_id')
        interval_bottom = int(interval_records_id.split('-')[0])
        interval_top = int(interval_records_id.split('-')[1])
        dict_['id_order_bulk'] = id_order_bulk
        dict_['interval_bottom'] = interval_bottom
        dict_['interval_top'] = interval_top        
        intervals.append(dict_)
       
    for interval in intervals:
        await db.execute("UPDATE records SET comment = $1 WHERE id BETWEEN $2 and $3", f"Оптовый заказ №{interval.get('id_order_bulk')}", interval.get('interval_bottom'), interval.get('interval_top'))

async def main():
    try:
        await db.connect()
        
        print(await add_delivery_to_bulk_order_from_id(db, 7, 100))
        
    except Exception as e:
        print(e)
    finally:
        await db.close()
        
if __name__=='__main__':
    asyncio.run(main())