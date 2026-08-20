import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.bot.database import db
import asyncio
from src.bot.utils.utils import *
from datetime import datetime, timezone, timedelta

async def delete_row(db, id_):
    
    await db.execute("DELETE FROM records WHERE id = $1", id_)

async def update_price_sell_for_specific_records(db, game, price_sell):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    
    await db.execute("UPDATE records SET price_sell = $2 WHERE game_id = $1 and status = 'Да'", games_id_dict[game], price_sell)

async def check_game_in_aviable(db, game):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    
    data = await db.fetch("SELECT * FROM records where game_id = $1 and status = 'Да'", games_id_dict[game])
    
    if len(data) < 1: return False
    else: return True

async def add_records(db, **kwargs):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    id_trns_dict, trns_id_dict = await get_trns_dict(db)
    
    if kwargs.get('game_id'):
        kwargs['game_id'] = games_id_dict[kwargs['game_id']]
        
    if kwargs.get('trns_id'):
        kwargs['trns_id'] = trns_id_dict[kwargs['trns_id']]
    
    columns = ", ".join(list(kwargs.keys()))
    
    placeholders = ", ".join(f"${i+1}" for i in range(len(kwargs)))
    
    values = list(kwargs.values())
    
    sql = f'INSERT INTO records ({columns}) VALUES ({placeholders})'
    
    await db.execute(sql, *values)  

async def update_records(db, **kwargs):
    
    id_ = kwargs.pop('id')
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    id_trns_dict, trns_id_dict = await get_trns_dict(db)
    
    if kwargs.get('game_id'):
        kwargs['game_id'] = games_id_dict[kwargs['game_id']]
        
    if kwargs.get('trns_id'):
        kwargs['trns_id'] = id_trns_dict[kwargs['trns_id']]
    
    placeholders = ", ".join([f'{key} = ${i}' for i, key in enumerate(list(kwargs.keys()), start=1)])
    
    sql = f"UPDATE records SET {placeholders} WHERE id = {id_}"
    
    values = list(kwargs.values())
    
    await db.execute(sql, *values)
    

async def main():
    try:
        await db.connect()
    
        # data = {
        #     'id' : 294,
        #     'buy_at': await get_today(),
        #     'sold_at': None,
        #     'game_id': '[PS4] (Б/У) ARK: Survival Evolved',
        #     'trns_id': None,
        #     'price_buy': 1000,
        #     'price_sell': 1200,
        #     'price_sold': None,
        #     'status': None,
        #     'swap': None,
        #     'reserve': None,
        #     'comment': None
        # }
        
        data = {
            'id' : 294,
            'price_buy': 1000,
            'price_sell': 999,
        }
            
        print(await update_records(db,**data))
        
    except Exception as e:
        print(e)
    finally:
        await db.close()
        
if __name__=='__main__':
    asyncio.run(main())