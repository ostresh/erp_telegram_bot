import asyncpg
from config import config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

class Database:
    def __init__(self):
        self.pool = None
        
    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(**config.DB_CONFIG)
            print("✅ Подключение к базе данных установлено")
        return self.pool
    
    async def close(self):
        if self.pool:
            await self.pool.close()
            print("❌ Подключение к базе данных закрыто")
            
    async def test_connection(self):
        try:
            async with self.pool.acquire() as connection:
                version = await connection.fetchval("SELECT version();")
                return f"✅ Подключено к PostgreSQL: {version}"
        except Exception as e:
            return f"❌ Ошибка подключения: {e}"
        
        
    async def execute(self, query: str, *args):
        '''Базовые запросы в бд'''
        async with self.pool.acquire() as connection:
            try:
                return await connection.execute(query, *args)
            except Exception as e:
                print(f'Ошибка: {e}')
    
    async def fetch(self, query: str, *args):
        """Получение нескольких строк"""
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def clear_data(self, table, *args):
        async with self.pool.acquire() as connection:
            return await connection.execute(f'TRUNCATE TABLE {table} RESTART IDENTITY CASCADE', *args)
            
db = Database()