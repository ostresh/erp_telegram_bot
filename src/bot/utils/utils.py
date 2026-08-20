from datetime import datetime, timezone, timedelta
import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.bot.app.messages.menu_messages import *
from src.bot.database import Database, db
import math

async def get_games_dict(db):
    games = await db.fetch('SELECT id, name FROM games_list ORDER BY id')
    return {game['id']: game['name'] for game in games}, {game['name']: game['id'] for game in games}

async def get_games_list(db):
    games = await db.fetch('SELECT name FROM games_list ORDER BY id')
    return [game['name'] for game in games]

async def get_trns_dict(db):
    utils = await db.fetch('SELECT id, title FROM trns_list ORDER BY id')
    return {util['id']: util['title'] for util in utils}, {util['title']: util['id'] for util in utils}

async def get_trns_list(db):
    utils = await db.fetch('SELECT title FROM trns_list ORDER BY id')
    return [util['title'] for util in utils]

async def get_games_tags_dict(db):
    games_tags = await db.fetch('SELECT * from games_tags ORDER BY game_id')
    return {tag['game_id']: tag['tag'] for tag in games_tags}

async def get_numbers(text):
    numbers = []
    current_num = ""
    
    for char in text:
        if char.isdigit():
            current_num += char
        else:
            if current_num:
                numbers.append(int(current_num))
                current_num = ""
    
    if current_num:
        numbers.append(int(current_num))
    
    return numbers

async def get_datetime_type_from_str(date):
    
    return datetime.strptime(date, "%d.%m.%Y")

async def get_str_type_from_datetime(date):
    
    return datetime.strftime(date, "%d.%m.%Y")

async def create_dataset_for_one_row(text):
    dataset = {}
    lines = text.strip().split('\n')

    for line in lines:
        try:
            key = line.split(':', 1)[0].strip()
            value = line.split(':', 1)[1].strip()
        except:
            key = line
            value = None
        # Преобразуем None строки в реальные None
        if value == '':
            value = None
        # Преобразуем числа в int
        elif key in ['ID', 'Цена покупки', 'Цена продажи', 'Цена продано']:
            if value is not None:
                value = int(value)
            else:
                value = 0
        
        elif key in ['Дата покупки', 'Дата продажи']:
            if value is not None:
                value = await get_datetime_type_from_str(value)
        
        # Сопоставляем русские ключи с английскими названиями полей
        key_mapping = {
            'ID': 'id',
            'Дата покупки': 'buy_at',
            'Дата продажи': 'sold_at',
            'Игра': 'game_id',
            'Транзакция': 'trns_id',
            'Цена покупки': 'price_buy',
            'Цена продажи': 'price_sell',
            'Цена продано': 'price_sold',
            'Статус': 'status',
            'Обмен': 'swap',
            'Бронь': 'reserve',
            'Комментарий': 'comment'
        }
        dataset[key_mapping.get(key, key)] = value
        
    return dataset

async def add_prefix_on_game_name(game):
    
    prefixes = ['[PS4] (Б/У) ', '[PS5] (Б/У) ', '[PS5] (НОВЫЙ) ', '[PS4] (НОВЫЙ) ']
    
    return [prefix + game for prefix in prefixes]

async def delete_prefix_from_game_name(game):
    
    prefixes = ['[PS4] (Б/У) ', '[PS5] (Б/У) ', '[PS5] (НОВЫЙ) ', '[PS4] (НОВЫЙ) ']
    
    
    for prefix in prefixes:
        game = game.replace(prefix, '')
        
    return game

async def delete_prefix_from_trns(trns_list):
    
    new_trns_list = []
    
    prefix = trns_list[0].split(' ')[0]
    
    for trns in trns_list:
        new_trns_list.append(trns.replace(f'{prefix} ', ''))
        
    return new_trns_list, prefix

async def get_today():
    
    return datetime.now(timezone(timedelta(hours=5))).date()

async def create_new_id_for_records(db):
    last_id = await db.fetch("SELECT MAX(id) as last_id from records")
    last_id = last_id[0].get('last_id')
    
    return last_id+1

async def row_sizes(total: int, max_len: int):
    """
    Возвращает список, в котором указано, сколько элементов будет в каждой «строке».
    Первый аргумент – общее число элементов, второй – максимальная длина строки.
    """
    rows_cnt = math.ceil(total / max_len)

    # Базовый размер строки и количество строк, которым нужно добавить 1 элемент.
    base_len = total // rows_cnt            # размер у «обычных» строк
    extra   = total % rows_cnt              # сколько строк будет на один элемент больше

    # Формируем список размеров: сначала более «полные» строки, потом обычные.
    sizes = [base_len + 1] * extra + [base_len] * (rows_cnt - extra)
    return sizes

# async def main():
#     print(await row_sizes(11, 4))
    
# asyncio.run(main())
    