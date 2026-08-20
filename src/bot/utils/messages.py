import math
from .emoji import Emoji
from src.bot.database import db
from .utils import get_games_dict, get_trns_dict
import re
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.bot.app.messages.menu_messages import MenuMessage

async def create_blocks_of_messages_records(data, block):
    
    id_games_dict, games_id_dict = await get_games_dict(db)
    id_trns_dict, trns_id_dict = await get_trns_dict(db)
    
    formatted_data = []
    
    for item in data:
        game_id = f"{Emoji.ID} <strong>{item.get('id')}</strong>" if item.get('id') is not None else ''
        buy_at = f" • {Emoji.DATE} {item.get('buy_at').strftime('%d.%m.%Y')}" if item.get('buy_at') is not None else ''
        sold_at = f" • {Emoji.DATE} {item.get('sold_at').strftime('%d.%m.%Y')}" if item.get('sold_at') is not None else ''
        trns = f"{Emoji.TRNS} <strong>{id_trns_dict[item.get('trns_id')]}</strong>" if item.get('trns_id') is not None else ''
        game = f"{Emoji.GAME} <strong>{id_games_dict[item.get('game_id')]}</strong>" if item.get('game_id') is not None else ''
        games_count = f"{Emoji.DISCS_COUNT} {item.get('games_count')} шт." if item.get('games_count') is not None else ''
        price_buy = f"{Emoji.PRICE_BUY} {item.get('price_buy')}р." if item.get('price_buy') is not None else f"{Emoji.PRICE_BUY} 0р."
        price_sell = f" • {Emoji.PRICE_SELL} {item.get('price_sell')}р." if item.get('price_sell') is not None else f" • {Emoji.PRICE_SELL} 0р."
        price_sold = f" •{Emoji.PRICE_SOLD} {item.get('price_sold')}р." if item.get('price_sold') is not None else f" • {Emoji.PRICE_SOLD} 0р."
        status = f"{Emoji.STATUS} {item.get('status')}" if item.get('status') is not None else ''
        swap = f"{Emoji.SWAP} {item.get('swap')}" if item.get('swap') is not None else ''
        reserve = f"{Emoji.RESERVE} {item.get('reserve')}" if item.get('reserve') is not None else ''
        comment = f"{Emoji.COMMENT} {item.get('comment')}" if item.get('comment') is not None else ''

    
        line1 = f"{game_id}{buy_at}{sold_at}".strip()
        line2 = f"{game}{trns}".strip()
        line3 = f"{games_count}".strip()
        line4 = f"{price_buy}{price_sell}{price_sold}".strip()
        line5 = f"{status}".strip()
        line6 = f"{swap}".strip()
        line7 = f"{reserve}".strip()
        line8 = f"{comment}".strip()
        
        formatted_item = '\n'.join(filter(None, [line1, line2, line3, line4, line5, line6, line7, line8]))
        formatted_item += MenuMessage.HORIZONTAL_LINE
        
        formatted_data.append(formatted_item)
    
    result = []
    
    [result.append(formatted_data[i*block:(i+1)*block]) for i in range(math.ceil(len(formatted_data)/block))]
    
    if block < 2: result = list(map(lambda item: "".join(item).strip(), result))
    else: result = list(map(lambda item: "".join(item).strip()[0:-len(MenuMessage.HORIZONTAL_LINE)+1].replace('\n\n', '\n').strip(), result))
        
    return result

async def create_block_of_messages_bulk_orders(data, block):
    
    formatted_data = []
    
    for item in data:
        order_id = f"{Emoji.ID} <strong>{item.get('id')}</strong>" if item.get('id') is not None else ''
        created_at = f" • {Emoji.DATE} {item.get('created_at').strftime('%d.%m.%Y')}" if item.get('created_at') is not None else ''
        arrived_at = f" • {Emoji.DATE} {item.get('arrived_at').strftime('%d.%m.%Y')}" if item.get('arrived_at') is not None else ''
        interval_id = f"{Emoji.INTERVAL_ID} <strong>{item.get('interval_records_id')}</strong>" if item.get('interval_records_id') is not None else ''
        seller = f"{Emoji.SELLER} <strong>{item.get('seller')}</strong>" if item.get('seller') is not None else ''
        status = f"{Emoji.STATUS} {item.get('order_status')}" if item.get('order_status') is not None else ''
        count = f"{Emoji.DISCS_COUNT} {item.get('total_count'):,} шт.".replace(',', '.') if item.get('total_count') is not None else f"{Emoji.DISCS_COUNT} 0 шт."
        cost = f"{Emoji.ORDER_BULK_COST} {item.get('total_cost'):,}р.".replace(',', '.') if item.get('total_cost') is not None else f'{Emoji.ORDER_BULK_COST} 0р.'
        delivery = f" • {Emoji.ORDER_BULK_DELIVERY_COST} {item.get('delivery_cost'):,}р.".replace(',', '.') if item.get('delivery_cost') is not None else f' • {Emoji.ORDER_BULK_DELIVERY_COST} 0р.'

        
        line1 = f"{order_id}{created_at}{arrived_at}".strip()
        line2 = f"{interval_id}".strip()
        line3 = f"{seller}".strip()
        line4 = f"{status}".strip()
        line5 = f"{count}".strip()
        line6 = f"{cost}{delivery}".strip()
        
        formatted_item = '\n'.join(filter(None, [line1, line2, line3, line4, line5, line6]))
        formatted_item += MenuMessage.HORIZONTAL_LINE
        
        formatted_data.append(formatted_item)

    result = []
        
    [result.append(formatted_data[i*block:(i+1)*block]) for i in range(math.ceil(len(formatted_data)/block))]
            
    if block < 2: result = list(map(lambda item: "".join(item).strip(), result))
    else: result = list(map(lambda item: "".join(item).strip()[0:-len(MenuMessage.HORIZONTAL_LINE)+1].replace('\n\n', '\n').strip(), result))
            
    return result

async def create_message_financial_indicators(db, data):
        
    incomes=f"{Emoji.INCOMES} <strong>ДОХОДЫ</strong> • <code>{data.get('incomes')}</code>р.\n" if data.get('incomes') else ''
    expences=f"{Emoji.EXPENCES} <strong>РАСХОДЫ</strong> • <code>{data.get('expences')}</code>р.\n" if data.get('expences') else ''
    avito=f"{Emoji.AVITO} <strong>АВИТО</strong> • <code>{data.get('avito')}</code>р.\n" if data.get('avito') else ''
    revenue=f"{Emoji.REVENUE} <strong>ВЫРУЧКА</strong> • <code>{data.get('revenue')}</code>р.\n" if data.get('revenue') else ''
    net_profit=f"{Emoji.NET_PROFIT} <strong>ЧИСТАЯ ПРИБЫЛЬ</strong> • <code>{data.get('net_profit')}</code>р.\n" if data.get('net_profit') else ''
    avg_revenue=f"{Emoji.AVG_REVENUE} <strong>СР. ВЫРУЧКА</strong> • <code>{data.get('avg_revenue')}</code>р.\n" if data.get('avg_revenue') else ''
    on_account=f"{Emoji.ON_ACCOUNT} <strong>НА СЧЕТУ</strong> • <code>{data.get('on_account')}</code>р.\n" if data.get('on_account') else ''
    discs_count=f"{Emoji.DISCS_COUNT} <strong>ДИСКОВ В НАЛИЧИИ</strong> • <code>{data.get('discs_count')}</code> шт.\n" if data.get('discs_count') else ''
    discs_count_sold=f"{Emoji.DISCS_COUNT_SOLD} <strong>ДИСКОВ ПРОДАНО</strong> • <code>{data.get('discs_count_sold')}</code> шт.\n" if data.get('discs_count_sold') else ''
    on_way = f"{Emoji.DELIVERY} <strong>ЕДЕТ К ПОКУПАТЕЛЮ</strong>\n{Emoji.ON_WAY} <code>{data.get('on_way')}</code>р." if data.get('on_way') else ''
    on_way_count = f" • {Emoji.ON_WAY_COUNT} <code>{data.get('on_way_count')}</code> шт.\n" if data.get('on_way_count') else ''
    all_assets = f"{Emoji.ALL_ASSETS} <strong>СУММА ВСЕХ АКТИВОВ</strong>\n• <code>{data.get('all_assets')}</code>р.\n" if data.get('all_assets') else ''

    line1 = f"{incomes}"
    line2 = f"{expences}"
    line3 = f"{avito}"
    line4 = f"{net_profit}"
    line5 = f"{revenue}"
    line6 = f"{avg_revenue}"
    line7 = f"{on_account}"
    line8 = f"{discs_count}"
    line9 = f"{discs_count_sold}"
    line10 = f"{on_way}{on_way_count}"
    line11 = f"{all_assets}"

    
    result = "\n".join(
    filter(None,
        [
            line1,
            line2,
            line3,
            line4,
            line5,
            line6,
            line7,
            line8,
            line9,
            line10,
            line11
        ],
    ))
    
    return result

async def change_message_group_games_by_prefixes(data):
    
    result = []
    
    current_prefix = '' 
    for message in data:
        block = message.split(MenuMessage.HORIZONTAL_LINE)
        new_block = []
        for item in block:
            prefix = re.findall(r'\[PS[45]\]\s*\((?:НОВЫЙ|Б/У)\)\s*', item)
            if prefix == current_prefix:
                item += MenuMessage.HORIZONTAL_LINE
            else:
                if current_prefix == '':
                    current_prefix = prefix
                    item = MenuMessage.HORIZONTAL_LINE + f"{Emoji.GROUP} <strong>{current_prefix[0].strip()}</strong>" + MenuMessage.HORIZONTAL_LINE + item + MenuMessage.HORIZONTAL_LINE
                else:
                    current_prefix = prefix
                    item = f"{Emoji.GROUP} <strong>{current_prefix[0].strip()}</strong>" + MenuMessage.HORIZONTAL_LINE + item + MenuMessage.HORIZONTAL_LINE
            new_block.append(item)
        result.append("".join(new_block).strip())
        
    return result 

async def divide_message_in_blocks(message, chars_in_one_block):
    
    result = []
    
    [result.append(message[i*chars_in_one_block:(i+1)*chars_in_one_block]) for i in range(math.ceil(len(message)/chars_in_one_block))]
    
    return result