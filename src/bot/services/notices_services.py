import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.bot.database import db
from src.bot.utils.utils import get_games_dict, get_games_tags_dict, delete_prefix_from_game_name, add_prefix_on_game_name
from src.bot.utils.messages import divide_message_in_blocks

async def create_general(db):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    id_games_tags_dict = await get_games_tags_dict(db)
    
    result = ''
    
    upper = await db.fetch("SELECT title from notice where name = 'header'")
    upper = f"{upper[0].get('title')}".replace('\\n', '\n').replace('  ', ' ')
    result += upper
    result += '\n\n📀 <strong>СПИСОК И ЦЕНЫ:</strong>\n'
    
    
    
    av_games_list = []
    av_games_query = await db.fetch("SELECT * from records where status = 'Да' and game_id is not null")
    [av_games_list.append([item.get('game_id'), item.get('price_sell')]) for item in av_games_query]
    av_games = sorted(list(set(list(map(lambda item: item.get('game_id'), av_games_query)))))
    
    # print(av_games)
    
    av_games_dict = {id_games_dict[item[0]] : item[1] for item in sorted(av_games_list)}
    
    av_ps4 = '\n🎯 <strong>ИГРЫ ДЛЯ PS4:</strong>\n'
    av_ps5 = '\n🎯 <strong>ИГРЫ ДЛЯ PS5:</strong>\n'
    
    for key, value in av_games_dict.items():
        if '[PS4]' in key:  
            av_ps4 += f'• <strong>{key}</strong> - {value} руб.\n'.replace('[PS4] ', '')
        elif '[PS5]' in key:
            av_ps5 += f'• <strong>{key}</strong> - {value}руб. \n'.replace('[PS5] ', '')
    result += av_ps5 + av_ps4
    
    basic_tags = await db.fetch("SELECT title from notice where name='base_tags'")
    basic_tags = basic_tags[0].get('title').replace('  ', ' ').replace('  ', ' ')
    result += '\nТеги для поиска:\n' + basic_tags
    
    personal_tags = "".join(list(set([id_games_tags_dict[item].replace('-', ' ') for item in av_games])))
    
    result += personal_tags
    
    if len(result) > 3900:
        result = await divide_message_in_blocks(result, 3900)
    else:
        result = [result]
    
    return result

async def create_for_new(db):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    id_games_tags_dict = await get_games_tags_dict(db)
    
    result = '❗ИГРЫ <strong>НОВЫЕ, ЗАПАКОВАННЫЕ, В ПЛЕНКЕ</strong>❗\n'
    
    upper = await db.fetch("SELECT title from notice where name = 'header'")
    upper = f"{upper[0].get('title')}".replace('\\n', '\n').replace('  ', ' ')
    result += upper
    result += '\n📀 <strong>СПИСОК И ЦЕНЫ:</strong>\n'
    
    
    
    av_games_list = []
    av_games_query = await db.fetch("SELECT * from records where status = 'Да' and game_id is not null")
    [av_games_list.append([item.get('game_id'), item.get('price_sell')]) for item in av_games_query]
    av_games = sorted(list(set(list(map(lambda item: item.get('game_id'), av_games_query)))))
    
    # print(av_games)
    
    av_games_dict = {id_games_dict[item[0]] : item[1] for item in sorted(av_games_list)}
    
    av_ps4 = '\n🎯 <strong>ИГРЫ ДЛЯ PS4:</strong>\n'
    av_ps5 = '\n🎯 <strong>ИГРЫ ДЛЯ PS5:</strong>\n'
    
    for key, value in av_games_dict.items():
        if '[PS4]' in key and 'НОВЫЙ' in key:  
            av_ps4 += f'• <strong>{key}</strong> - {value} руб.\n'.replace('[PS4] ', '')
        elif '[PS5]' in key and 'НОВЫЙ' in key:
            av_ps5 += f'• <strong>{key}</strong> - {value}руб. \n'.replace('[PS5] ', '')
    result += av_ps5 + av_ps4
    
    basic_tags = await db.fetch("SELECT title from notice where name = 'base_tags'")
    basic_tags = basic_tags[0].get('title').replace('  ', ' ').replace('  ', ' ')
    result += '\nТеги для поиска:\n' + basic_tags
    
    personal_tags = "".join(list(set([id_games_tags_dict[item].replace('-', ' ') for item in av_games])))
    
    result += personal_tags
    
    if len(result) > 3900:
        result = await divide_message_in_blocks(result, 3900)
    else:
        result = [result]
    
    return result

async def create_for_used(db):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    id_games_tags_dict = await get_games_tags_dict(db)
    
    result = ''
    
    upper = await db.fetch("SELECT title from notice where name = 'header'")
    upper = f"{upper[0].get('title')}".replace('\\n', '\n').replace('  ', ' ')
    result += upper
    result += '\n📀 <strong>СПИСОК И ЦЕНЫ:</strong>\n'
    
    
    
    av_games_list = []
    av_games_query = await db.fetch("SELECT * from records where status = 'Да' and game_id is not null")
    [av_games_list.append([item.get('game_id'), item.get('price_sell')]) for item in av_games_query]
    av_games = sorted(list(set(list(map(lambda item: item.get('game_id'), av_games_query)))))
    
    # print(av_games)
    
    av_games_dict = {id_games_dict[item[0]] : item[1] for item in sorted(av_games_list)}
    
    av_ps4 = '\n🎯 <strong>ИГРЫ ДЛЯ PS4:</strong>\n'
    av_ps5 = '\n🎯 <strong>ИГРЫ ДЛЯ PS5:</strong>\n'
    
    for key, value in av_games_dict.items():
        if '[PS4]' in key and 'НОВЫЙ' not in key:  
            av_ps4 += f'• <strong>{key}</strong> - {value} руб.\n'.replace('[PS4] ', '')
        elif '[PS5]' in key and 'НОВЫЙ' not in key:
            av_ps5 += f'• <strong>{key}</strong> - {value}руб. \n'.replace('[PS5] ', '')
    result += av_ps5 + av_ps4
    
    basic_tags = await db.fetch("SELECT title from notice where name = 'base_tags'")
    basic_tags = basic_tags[0].get('title').replace('  ', ' ').replace('  ', ' ')
    result += '\nТеги для поиска:\n' + basic_tags
    
    personal_tags = "".join(list(set([id_games_tags_dict[item].replace('-', ' ') for item in av_games])))
    
    result += personal_tags
    
    if len(result) > 3900:
            result = await divide_message_in_blocks(result, 3900)
    else:
            result = [result]
    
    return result

async def create_personal(db, game):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    
    result = ''
    
    upper = await db.fetch("SELECT title from notice where name = 'header'")
    upper = f"{upper[0].get('title')}".replace('\\n', '\n').replace('  ', ' ')
    result += upper + '\n\n\n\n'
    
    notice_for_personal_tags = await db.fetch("SELECT title from notice where name = 'base_personal_tags'")
    
    result += notice_for_personal_tags[0].get('title')
    
    personal_tags = await db.fetch(f"SELECT tag from games_tags where game_id = $1", games_id_dict[game])
    
    result += personal_tags[0].get('tag')
    
    return result

async def get_personal_tag(db, game):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    
    personal_tags = await db.fetch(f"SELECT tag from games_tags where game_id = $1", games_id_dict[game])
    
    return personal_tags[0].get('tag')

async def change_personal_tag(db, game, tag):
    
    game_without_perfixes = await delete_prefix_from_game_name(game)
    
    game_with_prefixes = await add_prefix_on_game_name(game_without_perfixes)
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    
    for item in game_with_prefixes:
        try:
            await db.execute("UPDATE games_tags SET tag = $1 WHERE game_id = $2", tag, games_id_dict[item])
        except KeyError:
            ...

async def get_base_for_notice(db, name):
        
    base_description = await db.fetch(f"SELECT title from notice where name = $1", name)
    
    return base_description[0].get('title')

async def change_base_for_description(db, base, new_title):
    
    await db.execute("UPDATE notice SET title = $1 WHERE name = $2", new_title, base) 
    
async def main():
    try:
        await db.connect()
        
        print(await create_for_new(db))
        
    except Exception as e:
        print(e)
    finally:
        await db.close()
    
if __name__=='__main__':
    asyncio.run(main())