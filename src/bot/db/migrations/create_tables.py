import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.bot.database import db_sql


sql_query = '''
    -- Создание таблицы GAMES_LIST
CREATE TABLE IF NOT EXISTS games_list (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL
);

-- Создание таблицы UTILS_LIST  
CREATE TABLE IF NOT EXISTS utils_list (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL
);

-- Создание таблицы GAMES_TAGS
CREATE TABLE IF NOT EXISTS games_tags (
    game_id INTEGER NOT NULL REFERENCES games_list(id),
    tag TEXT NOT NULL,
    PRIMARY KEY (game_id, tag)
);

-- Создание таблицы RECORDS
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY,
    purchase_at TIMESTAMP,
    sold_at TIMESTAMP,
    
    -- Поля для связи с играми и утилитами
    game_id INTEGER REFERENCES games_list(id) ON DELETE SET NULL,
    trns_id INTEGER REFERENCES utils_list(id) ON DELETE SET NULL,
    
    price_purchase INTEGER,
    price_selling INTEGER,
    price_sold INTEGER,
    
    status VARCHAR(50),
    swap VARCHAR(20),
    reserve TEXT,
    comment TEXT,
    
    -- Проверка, что указана либо игра, либо утилита, но не оба одновременно
    CONSTRAINT check_game_or_util CHECK (
        (game_id IS NOT NULL AND trns_id IS NULL) OR 
        (game_id IS NULL AND trns_id IS NOT NULL)
    )
);
    '''

async def create_tables(query):
    
    await db_sql.connect()
    try:
        await db_sql.execute(query)
        print('✅ Таблицы успешно созданы!')
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        return False
    finally:
        await db_sql.close()

async def main():
    await create_tables(query=sql_query)
        
if __name__=='__main__':
    asyncio.run(main())
    
    
