import sys
import os
import csv
import asyncio
import pandas as pd
import json
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.bot.database import db
from src.bot.utils.utils import *
from src.bot.services.bulk_orders_services import change_records_comments_from_bulk_orders

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

async def clear_data(table):
    await db.clear_data(table)
    print(f"🗑️ Таблица {table} очищена")
        
async def load_games_list(db):

    with open('data/games_list.csv', 'r', encoding='UTF-8', newline='') as f:
        csv_list = csv.reader(f)
    
        data = [','.join(row) for row in csv_list]
        
    data = sorted(list(set(data)))
        
    for item in data:
        try:
            await db.execute('INSERT INTO games_list (name) VALUES ($1)', item)
            print(f'✅ Объект {item} успешно записан!')
        except Exception as e:
            print(f"❌ Ошибка: {e}")

async def load_utils_list(db):
    
    data = ['[UTIL] Зачисление/вывод средств', '[UTIL] Авито', '[UTIL] Покупка']
    
    for item in data:
        try:
            await db.execute('INSERT INTO utils_list (title) VALUES ($1)', item)
            print(f'✅ Объект {item} успешно записан!')
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
async def load_tags(db):
    with open('data/tags.csv', 'r', encoding='UTF-8', newline='') as f:
        csv_list = csv.reader(f)
        next(csv_list)
    
        data = list(csv_list)
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    games_list = await get_games_list(db)
    
    
    data_dict = {item[0]: item[1] for item in data}    
    
    for game in games_list:
        try:
            tag = data_dict[game.replace(':', '').replace('"', '')]
            await db.execute('INSERT INTO games_tags (game_id, tag) VALUES ($1, $2)', games_id_dict[game], tag)
            print(f"✅ Объект {game} успешно записан!")
        except Exception as e:
            print(f'ERROR {e}')

async def load_records(db):
    with open('data/records.csv', 'r', encoding='UTF-8', newline='',) as f:
        csv_list = csv.reader(f, delimiter=',')
        next(csv_list)
        data = list(csv_list)
    
    await db.execute('TRUNCATE TABLE records RESTART IDENTITY CASCADE')
    
    result = []
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    id_trns_dict, trns_id_dict = await get_trns_dict(db)
     
    for item in data:
        if len(item[2]) < 1:
            continue
        try:
            temp_dict = {}
            temp_dict['buy_at'] = datetime.strptime(item[1], "%d.%m.%Y")
            temp_dict['sold_at'] = None
            try:
                temp_dict['game_id'] = games_id_dict[item[2]]
                temp_dict['trns_id'] = None
            except:   
                temp_dict['game_id'] = None
                temp_dict['trns_id'] = trns_id_dict[item[2]]
            temp_dict['price_buy'] = int(item[4].split(',')[0]) if len(item[4]) > 0 else 0
            temp_dict['price_sell'] = int(item[3].split(',')[0]) if len(item[3]) > 0 else 0
            temp_dict['price_sold'] = int(item[5].split(',')[0]) if len(item[5]) > 0 else 0
            if item[8] == 'Едет к покупателю':
                temp_dict['status'] = "Едет к покупателю"
            else:
                temp_dict['status'] = item[7] if len(item[7]) > 0 else 'Да'
            temp_dict['swap'] = item[9] if len(item[9]) > 0 else None
            temp_dict['reserve'] = item[10] if len(item[10]) > 0 else None
            temp_dict['comment'] = item[11] if len(item[11]) > 0 else None
        except Exception as e:
            print(f'{item[0]}, ОШИБКА: {e}')
        result.append(temp_dict)
        
    counter = 3
    counter_errors = 0    
    for game in result:
        try:
            await db.execute('INSERT INTO records (id, buy_at, sold_at, game_id, trns_id, price_buy, price_sell, price_sold, status, swap, reserve, comment) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)', counter, game['buy_at'], game['sold_at'], game['game_id'], game['trns_id'], game['price_buy'], game['price_sell'], game['price_sold'], game['status'], game['swap'], game['reserve'], game['comment'])
            if game['game_id'] is None:
                print(f"✅ Объект {counter} | {id_trns_dict[game['trns_id']]} успешно записан!")
            else:
                print(f"✅ Объект {counter} | {id_games_dict[game['game_id']]} успешно записан!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            counter_errors +=1
        counter += 1
    # print(counter_errors)
    
    await change_records_comments_from_bulk_orders(db)
    
    return
        
    
async def main():
    try:
        await db.connect()
        # await clear_data('games_list')
        # await load_games_list(db)
        # await load_trns_list(db)
        # await load_tags(db)
        await load_records(db)
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        await db.close()
    
if __name__=='__main__':
    asyncio.run(main())
    
