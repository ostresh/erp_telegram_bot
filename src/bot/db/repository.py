from datetime import datetime, timezone
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
from db.models import Record, Game, Utility, RecordStatus, BulkOrder
from src.bot.db.status.status import RecordStatus, BulkOrderStatus


class GameRepository:
    """Репозиторий для работы с играми"""
    
    @staticmethod
    async def get_all(session: AsyncSession) -> List[Game]:
        """Получить все игры"""
        stmt = select(Game).order_by(Game.name)
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(session: AsyncSession, game_id: int) -> Optional[Game]:
        """Получить игру по ID"""
        stmt = select(Game).where(Game.id == game_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_name(session: AsyncSession, name: str) -> Optional[Game]:
        """Получить игру по названию"""
        stmt = select(Game).where(Game.name == name)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def search_by_name(session: AsyncSession, query: str) -> List[Game]:
        """Поиск игр по названию (LIKE)"""
        stmt = select(Game).where(Game.name.ilike(f"%{query}%")).order_by(Game.name)
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(session: AsyncSession, name: str) -> Game:
        """Создать новую игру"""
        game = Game(name=name)
        session.add(game)
        await session.flush()
        return game


class UtilityRepository:
    """Репозиторий для работы с утилитами"""
    
    @staticmethod
    async def get_all(session: AsyncSession) -> List[Utility]:
        """Получить все утилиты"""
        stmt = select(Utility).order_by(Utility.title)
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(session: AsyncSession, util_id: int) -> Optional[Utility]:
        """Получить утилиту по ID"""
        stmt = select(Utility).where(Utility.id == util_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_title(session: AsyncSession, title: str) -> Optional[Utility]:
        """Получить утилиту по названию"""
        stmt = select(Utility).where(Utility.title == title)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


class RecordRepository:
    """Репозиторий для работы с записями"""
    
    @staticmethod
    async def get_by_id(
        session: AsyncSession, 
        record_id: int,
        with_relations: bool = True
    ) -> Optional[Record]:
        """Получить запись по ID"""
        stmt = select(Record).where(Record.id == record_id)
        
        if with_relations:
            stmt = stmt.options(
                selectinload(Record.game),
                selectinload(Record.utility)
            )
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_available(
        session: AsyncSession,
        with_relations: bool = True
    ) -> List[Record]:
        """Получить все доступные записи"""
        stmt = select(Record).where(Record.status == RecordStatus.AVAILABLE.value)
        
        if with_relations:
            stmt = stmt.options(selectinload(Record.game))
        
        stmt = stmt.order_by(Record.purchase_at.desc())
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_game(
        session: AsyncSession,
        game_name: str,
        status: Optional[str] = None
    ) -> List[Record]:
        """Получить записи по названию игры"""
        stmt = (
            select(Record)
            .join(Game)
            .where(Game.name.ilike(f"%{game_name}%"))
            .options(selectinload(Record.game))
        )
        
        if status:
            stmt = stmt.where(Record.status == status)
        
        stmt = stmt.order_by(Record.id.desc())
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(session: AsyncSession, record: Record) -> Record:
        """Создать новую запись"""
        session.add(record)
        await session.flush()
        return record
    
    @staticmethod
    async def update(
        session: AsyncSession,
        record_id: int,
        **kwargs
    ) -> Optional[Record]:
        """Обновить запись"""
        stmt = (
            update(Record)
            .where(Record.id == record_id)
            .values(**kwargs)
            .returning(Record)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete(session: AsyncSession, record_id: int) -> bool:
        """Удалить запись"""
        stmt = delete(Record).where(Record.id == record_id)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount > 0
    
    @staticmethod
    async def update_price_for_game(
        session: AsyncSession,
        game_name: str,
        new_price: int
    ) -> int:
        """Обновить цену продажи для всех доступных записей игры"""
        stmt = (
            update(Record)
            .where(
                and_(
                    Record.game_id == Game.id,
                    Game.name == game_name,
                    Record.status == RecordStatus.AVAILABLE.value
                )
            )
            .values(price_selling=new_price)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount

class BulkOrderRepository:
    """Репозиторий для работы с оптовыми заказами"""
    
    @staticmethod
    async def get_by_id(session: AsyncSession, order_id: int) -> Optional[BulkOrder]:
        stmt = select(BulkOrder).where(BulkOrder.id == order_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(session: AsyncSession) -> List[BulkOrder]:
        stmt = select(BulkOrder).order_by(BulkOrder.created_at.desc())
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_status(
        session: AsyncSession,
        status: str
    ) -> List[BulkOrder]:
        stmt = (
            select(BulkOrder)
            .where(BulkOrder.order_status == status)
            .order_by(BulkOrder.created_at.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def create(session: AsyncSession, order: BulkOrder) -> BulkOrder:
        session.add(order)
        await session.flush()
        return order
    
    @staticmethod
    async def update(
        session: AsyncSession,
        order_id: int,
        **kwargs
    ) -> Optional[BulkOrder]:
        stmt = (
            update(BulkOrder)
            .where(BulkOrder.id == order_id)
            .values(**kwargs)
            .returning(BulkOrder)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete(session: AsyncSession, order_id: int) -> bool:
        stmt = delete(BulkOrder).where(BulkOrder.id == order_id)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount > 0
    
    @staticmethod
    async def mark_as_arrived(
        session: AsyncSession,
        order_id: int
    ) -> Optional[BulkOrder]:
        """Отметить заказ как прибывший"""
        stmt = (
            update(BulkOrder)
            .where(BulkOrder.id == order_id)
            .values(
                arrived_at=datetime.now(timezone.utc),
                order_status=BulkOrderStatus.ARRIVED.value
            )
            .returning(BulkOrder)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.scalar_one_or_none()