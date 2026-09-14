from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, exists, func, case, and_
from sqlalchemy.orm import selectinload
from typing import List, Tuple, Optional

from bot.db.models import Record, Game, Utility
from bot.db.repository.base import BaseRepository
from bot.db.status.status import RecordStatus

import logging

logger = logging.getLogger(__name__)

class RecordRepository(BaseRepository[Record]):
    """Репозиторий для Record. Наследует базовые CRUD, добавляет специфичные методы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Record)
    
    
    async def is_game_available(self, game_name: str) -> bool:
        """
        Проверка, есть ли игра в наличии
        
        Args:
            game_name - название игры
        
        Return:
            Bool есть ли игра
            
        Raises:
            Exception: При ошибке создания
        """
        
        logger.debug(f"Checking availability for game '{game_name}'")
        
        try:
            stmt = select(
            exists(
                select(Record.id)
                .join(Game, Record.game_id == Game.id)
                .where(
                    Game.name == game_name,
                    Record.status == RecordStatus.AVAILABLE.value
                )
            ))
            result = await self.session.execute(stmt)
            available = result.scalar()
            
            logger.debug(f"Game '{game_name}' available: {available}")
            return available
        except Exception as e:
            logger.debug(f"Error checking availability for game '{game_name}': {e}")
            raise
    
    async def get_available_games(self) -> List[Tuple[str, int, int]]:
        """
        Получение всех игр из наличия
        С группировкой по играм
        
        Return:
            Список Record
            
        Raises:
            Exception: При ошибке создания
        """
        
        logger.debug("Getting available games")
        
        try:
            stmt = (
                select(Game.name, Record.price_purchase, Record.price_selling)
                .join(Game, Record.game_id == Game.id)
                .where(Record.status == RecordStatus.AVAILABLE.value)
                .group_by(Game.name, Record.price_purchase, Record.price_selling)
                .order_by(Game.name)
            )
            result = await self.session.execute(stmt)
            games = result.all()
            
            logger.debug(f"Retrieved {len(games)} available games")
            return games
        except Exception as e:
            logger.debug(f"Error getting available games: {e}")
            raise
    
    async def get_delivery_to_me(self) -> List[Record]:
        """
        Получение всех записей
        Которые едут ко мне
        
        Return:
            Список Record
        
        Raises:
            Exception: При ошибке создания
        """
        
        logger.debug("Getting dilevery to me records")
        
        try:
            stmt = (
                select(Record)
                .where(
                    Record.status == RecordStatus.DELIVERY_TO_ME.value
                )
                .order_by(Record.id.asc())
            )
            result = await self.session.execute(stmt)
            records = result.scalars().all()
        
            logger.debug(f"Retrieved {len(records)} delivery to me records")
            return records
        except Exception as e:
            logger.debug(f"Error getting delivery to me records {e}")
            raise
        
    async def get_delivery_to_client(self) -> List[Record]:
        """
        Получение всех записей
        Которые едут к покупателю
        
        Return:
            Список Record
        
        Raises:
            Exception: При ошибке создания
        """
        
        logger.debug("Getting dilevery to client records")
        
        try:
            stmt = (
                select(Record)
                .where(
                    Record.status == RecordStatus.DELIVERY_TO_CLIENT.value
                )
                .order_by(Record.id.asc())
            )
            result = await self.session.execute(stmt)
            records = result.scalars().all()
        
            logger.debug(f"Retrieved {len(records)} delivery to client records")
            return records
        except Exception as e:
            logger.debug(f"Error getting delivery to client records: {e}")
            raise
        
    
    async def update_price_selling_for_games(self, game_name: str, new_price: int) -> int:
        """
        Обновляет цену продажи для всех доступных записей игры
        
        Args:
            game_name - название игры
            new_price - цена
            
        Return:
            количество измененных строк или None
            
        Raises:
            Exception: При ошибке создания
        """
        
        logger.debug(f"Updating price for game '{game_name}' to {new_price}")
        
        try:
            stmt = (
                update(Record)
                .where(
                    Record.status == RecordStatus.AVAILABLE.value,
                    Record.game_id.in_(
                        select(Game.id).where(Game.name == game_name)
                    )
                )
                .values(price_selling=new_price)
            )
            
            result = await self.session.execute(stmt)
            await self.session.flush()
            
            count = result.rowcount
            
            is_updated = count > 0
            
            if is_updated:      
                logger.debug(f"Updated price for {count} records of game '{game_name}'")
            else:
                logger.debug(f"Available {game_name} in records not found")
            return count
        except Exception as e:
            logger.debug(f"Error updating price for game '{game_name}': {e}")
            raise
    
    async def get_by_bulk_order_id(self, order_id: int) -> List[Record]:
        """
        Получение всех записей,
        связанных с оптовым заказом
        
        Args:
            order_id - id оптового заказа
        
        Return:
            Список Record
        
        Raises:
            Exception: При ошибке получения
        """
        logger.debug(f"Getting records for bulk order id={order_id}")
        
        try:
            stmt = (
                select(Record)
                .where(Record.bulk_order_id == order_id)
                .order_by(Record.id.asc())
            )
            result = await self.session.execute(stmt)
            records = result.scalars().all()
            
            logger.debug(f"Retrieved {len(records)} records for bulk order id={order_id}")
            return records
        except Exception as e:
            logger.debug(f"Error getting records for bulk order id={order_id}: {e}")
            raise
        
    async def get_by_id_with_relations(self, item_id: int) -> Optional[Record]:
        """
        Получение записи по id с загруженными связями
        (игра и транзакция) для полного вывода информации
        
        Args:
            item_id - id записи
        
        Return:
            Объект Record с загруженными связями или None
        
        Raises:
            Exception: При ошибке получения
        """
        logger.debug(f"Getting Record by id={item_id} with relations")
        
        try:
            stmt = (
                select(Record)
                .options(
                    selectinload(Record.game),
                    selectinload(Record.utility)
                )
                .where(Record.id == item_id)
            )
            result = await self.session.execute(stmt)
            item = result.scalar()
            
            if item:
                logger.debug(f"Record with id={item_id} found (with relations)")
            else:
                logger.debug(f"Record with id={item_id} not found")
            
            return item
        except Exception as e:
            logger.debug(f"Error getting Record by id={item_id} with relations: {e}")
            raise
    
     
    """
    Запросы для финансового отчета
    Сгруппированы по смыслу запроса
    """
    async def get_expenses_incomes_financials(self) -> Tuple[int, int]:
        """
        Получить базовые доходы и расходы одним запросом.
        
        Return:
            Кортеж (expenses, incomes)
        """
        logger.debug("Getting expenses and incomes financials")
        
        try:
            stmt = select(
                # Расходы: сумма всех закупок
                func.coalesce(func.sum(Record.price_purchase), 0).label('expenses'),
                
                # Доходы: сумма продаж со статусами 'Нет' и 'Едет ко мне'
                func.coalesce(func.sum(
                    case(
                        (Record.status.in_([
                            RecordStatus.SOLD.value,
                            RecordStatus.DELIVERY_TO_ME.value
                        ]), Record.price_sold),
                        else_=0
                    )
                ), 0).label('incomes')
            )
            
            result = await self.session.execute(stmt)
            row = result.one()
            
            expenses = row.expenses
            incomes = row.incomes
            logger.debug(f"expenses={expenses}, incomes={incomes}")
            return expenses, incomes
            
        except Exception as e:
            logger.debug(f"Error getting expenses and incomes financials: {e}")
            raise
    
    async def get_sales_financials(self) -> Tuple[int, int]:
        """
        Получить выручку по играм и количество проданных дисков одним запросом.
        
        Выручка - грязная разница доходов и расходов по играм.
        
        Return:
            Кортеж (revenue, discs_count_sold)
        """
        logger.debug("Getting sales financials (revenue, discs_count_sold)")
        
        try:
            stmt = select(
                # Выручка: разница для игр (статусы 'Нет' и 'Едет к покупателю')
                func.coalesce(func.sum(
                    case(
                        (and_(
                            Record.game_id.isnot(None),
                            Record.status.in_([
                                RecordStatus.SOLD.value,
                                RecordStatus.DELIVERY_TO_CLIENT.value
                            ])
                        ), Record.price_sold - Record.price_purchase),
                        else_=0
                    )
                ), 0).label('revenue'),
                
                # Количество проданных дисков (только игры, без транзакций)
                func.count(
                    case(
                        (and_(
                            Record.status == RecordStatus.SOLD.value,
                            Record.game_id.isnot(None),
                            Record.trns_id.is_(None)
                        ), Record.id)
                    )
                ).label('discs_count_sold')
            )
            
            result = await self.session.execute(stmt)
            row = result.one()
            
            revenue = row.revenue
            discs_count_sold = row.discs_count_sold
            logger.debug(f"Sales financials: revenue={revenue}, sold={discs_count_sold}")
            return revenue, discs_count_sold
            
        except Exception as e:
            logger.debug(f"Error getting sales financials: {e}")
            raise
    
    async def get_delivery_to_client_financial(self) -> Tuple[int, int]:
        """
        Получить сумму и количество записей, едущих к покупателю.
        
        Возвращает и сумму, и количество одним запросом,
        так как у них одинаковое условие фильтрации.
        
        Return:
            Кортеж (on_way, on_way_count)
        """
        logger.debug("Getting delivery to client (sum, count)")
        
        try:
            stmt = select(
                func.coalesce(func.sum(Record.price_sold), 0).label('on_way'),
                func.count(Record.id).label('on_way_count')
            ).where(
                and_(
                    Record.status == RecordStatus.DELIVERY_TO_CLIENT.value,
                    Record.game_id.isnot(None)
                )
            )
            
            result = await self.session.execute(stmt)
            row = result.one()
            
            on_way = row.on_way
            on_way_count = row.on_way_count
            logger.debug(f"Delivery to client: sum={on_way}, count={on_way_count}")
            return on_way, on_way_count
            
        except Exception as e:
            logger.debug(f"Error getting delivery to client: {e}")
            raise
    
    async def count_available_discs(self) -> int:
        """
        Подсчитать количество дисков в наличии.
        
        Return:
            Количество дисков со статусом 'Да'
        """
        logger.debug("Counting available discs")
        
        try:
            stmt = select(func.count(Record.id)).where(
                Record.status == RecordStatus.AVAILABLE.value
            )
            
            result = await self.session.execute(stmt)
            count = result.scalar()
            
            logger.debug(f"Available discs: {count}")
            return count
            
        except Exception as e:
            logger.debug(f"Error counting available discs: {e}")
            raise
    
    async def get_assets_value(self) -> Tuple[int, int]:
        """
        Получить стоимость товаров в наличии и 'едет ко мне' одним запросом.
        
        Берёт цену продажи, если она есть, иначе цену покупки.
        
        Return:
            Кортеж (available_sum, coming_to_me_sum)
        """
        logger.debug("Getting assets value (available, coming_to_me)")
        
        try:
            # Цена: сначала продажная, иначе закупочная
            price = func.coalesce(Record.price_selling, Record.price_purchase)
            
            stmt = select(
                # Стоимость в наличии
                func.coalesce(func.sum(
                    case(
                        (Record.status == RecordStatus.AVAILABLE.value, price),
                        else_=0
                    )
                ), 0).label('available_sum'),
                
                # Стоимость 'едет ко мне'
                func.coalesce(func.sum(
                    case(
                        (Record.status == RecordStatus.DELIVERY_TO_ME.value, price),
                        else_=0
                    )
                ), 0).label('coming_to_me_sum')
            )
            
            result = await self.session.execute(stmt)
            row = result.one()
            
            available_sum = row.available_sum
            coming_to_me_sum = row.coming_to_me_sum
            logger.debug(f"Assets: available={available_sum}, coming={coming_to_me_sum}")
            return available_sum, coming_to_me_sum
            
        except Exception as e:
            logger.debug(f"Error getting assets value: {e}")
            raise
    
    async def get_expenses_by_transaction(self, transaction_title: str) -> int:
        """
        Получить расходы по конкретной транзакции (например, Авито).
        
        Требует JOIN с таблицей utilities.
        
        Return:
            Сумма расходов по транзакции
        """
        logger.debug(f"Getting expenses for transaction '{transaction_title}'")
        
        try:
            stmt = select(
                func.coalesce(func.sum(Record.price_purchase), 0)
            ).join(
                Utility, Record.trns_id == Utility.id
            ).where(
                Utility.title.ilike(f'%{transaction_title}%')
            )
            
            result = await self.session.execute(stmt)
            expenses = result.scalar()
            
            logger.debug(f"Expenses for '{transaction_title}': {expenses}")
            return expenses
            
        except Exception as e:
            logger.debug(f"Error getting expenses by transaction: {e}")
            raise