import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database import db
import asyncio
from utils.utils import get_games_dict, get_numbers, get_trns_dict, create_dataset_for_one_row, add_prefix_on_game_name, delete_prefix_from_game_name
from datetime import datetime, timezone, timedelta


async def add_game_in_game_list(db, game, tag):
    
    game_with_prefixes = await add_prefix_on_game_name(game)
    
    for item in game_with_prefixes:
        await db.execute('INSERT INTO games_list (name) VALUES ($1)', item)
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    
    for item in game_with_prefixes:
        await db.execute('INSERT INTO games_tags (game_id, tag) VALUES ($1, $2)', games_id_dict[item], tag)

async def check_game_in_game_list(db, game):
    
    check = await db.fetch("SELECT * FROM public.games_list where name ilike $1", f"%{game}%")

    if len(check) == 0: return False
    else: return True

async def delete_game_from_game_list(db, game):
    
    game = await delete_prefix_from_game_name(game)
    
    await db.execute("DELETE FROM public.games_tags WHERE game_id IN (SELECT id FROM public.games_list WHERE name ILIKE $1)", f"%{game}%")
    await db.execute("DELETE FROM public.records WHERE game_id IN (SELECT id FROM public.games_list WHERE name ILIKE $1)", f"%{game}%")
    await db.execute("DELETE FROM public.games_list WHERE name ILIKE $1", f"%{game}%")


async def main():
    try:
        await db.connect()
        
        print(await add_prefix_on_game_name('Atomic Heart'))
        
        # print(await delete_game_from_game_list(db, '[PS5] (НОВЫЙ) Atomic Heart'))
        
    except Exception as e:
        print(e)
    finally:
        await db.close()
        
if __name__=='__main__':
    asyncio.run(main())