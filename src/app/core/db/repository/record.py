from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, exists, func, case, and_
from sqlalchemy.orm import selectinload
from typing import List, Tuple, Optional

from app.core.db.models import Record, Game, Utility
from app.core.db.repository.base import BaseRepository
from app.core.db.statuses import RecordStatus

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
            Exception: При ошибке чтения
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
            logger.exception(f"Error checking availability for game '{game_name}': {e}")
            raise
    
    async def get_available(self) -> List[Tuple[Record, str]]:
        """
        Получение всех игр из наличия
        С группировкой по играм
        
        Return:
            Список кортежей Record + название игры
            
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.debug("Getting available records")
        
        try:
            stmt = (
                select(Record, Game.name)
                .join(Game, Record.game_id == Game.id)
                .where(Record.status == RecordStatus.AVAILABLE.value)
                .group_by(Record.id, Game.name)
                .order_by(Record.id)
            )
            result = await self.session.execute(stmt)
            records = result.all()
            
            logger.debug(f"Retrieved {len(records)} available records")
            return records
        except Exception as e:
            logger.exception(f"Error getting available records: {e}")
            raise
    
    async def get_in_transit_to_me(self) -> List[Record]:
        """
        Получение всех записей
        Которые едут ко мне
        
        Return:
            Список Record
        
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.debug("Getting delivery to me records")
        
        try:
            stmt = (
                select(Record)
                .where(
                    Record.status == RecordStatus.IN_TRANSIT_TO_ME.value
                )
                .order_by(Record.id.asc())
            )
            result = await self.session.execute(stmt)
            records = result.scalars().all()
        
            logger.debug(f"Retrieved {len(records)} delivery to me records")
            return records
        except Exception as e:
            logger.exception(f"Error getting delivery to me records {e}")
            raise
        
    async def get_in_transit_to_client(self) -> List[Record]:
        """
        Получение всех записей
        Которые едут к покупателю
        
        Return:
            Список Record
        
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.debug("Getting delivery to client records")
        
        try:
            stmt = (
                select(Record)
                .where(
                    Record.status == RecordStatus.IN_TRANSIT_TO_CLIENT.value
                )
                .order_by(Record.id.asc())
            )
            result = await self.session.execute(stmt)
            records = result.scalars().all()
        
            logger.debug(f"Retrieved {len(records)} delivery to client records")
            return records
        except Exception as e:
            logger.exception(f"Error getting delivery to client records: {e}")
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
            Exception: При ошибке обновления
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
            logger.exception(f"Error updating price for game '{game_name}': {e}")
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
            Exception: При ошибке чтения
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
            logger.exception(f"Error getting records for bulk order id={order_id}: {e}")
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
            logger.exception(f"Error getting Record by id={item_id} with relations: {e}")
            raise
    
    
    async def get_price_selling_for_game_in_available(self, game_name: str) -> int:
        """
        Получение цены продажи для конкретной игры из наличия
        
        Args:
            game_name: Название игры
            
        Returns:
            Цену для продажи, если:
                Конкретная игра в наличии
                Для этой игры установлена цена (не 0)
            Если цена не установлена, вернет 0
        """
        
        logger.debug(f'Getting price_sell for game in available: {game_name}')
        
        try:
            
            stmt = (
                select(func.max(Record.price_selling))
                .join(Game, Record.game_id == Game.id)
                .where(
                    and_(
                        Record.status == RecordStatus.AVAILABLE,
                        Game.name == game_name
                    )
                )
            )
            
            result = await self.session.execute(stmt)
            price_selling = result.scalar_one_or_none()
            
            if price_selling is None:
                price_selling = 0
            
            logger.debug(f'Retrieved price_selling {price_selling} for game: {game_name}')
            
            return price_selling
            
        except Exception as e:
            logger.exception(f'Error getting price_sell for game {game_name} in available : {e}')
            raise
    
    async def get_available_by_game(self, game_name: str) -> List[Record]:
        """
        Получение всех записей из наличия определенной игры
        С группировкой по записям
        
        Args:
            game_name: название игры
        
        Return:
            Список Record
            
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.debug(f"Getting available records by game: {game_name}")
        
        try:
            stmt = (
                select(Record)
                .join(Game, Record.game_id == Game.id)
                .where(
                    and_(
                        Record.status == RecordStatus.AVAILABLE.value,
                        Game.name == game_name
                    )
                )
                .order_by(Record.id.asc())
            )
            result = await self.session.execute(stmt)
            records = result.scalars().all()
            
            logger.debug(f"Retrieved {len(records)} available records")
            return records
        except Exception as e:
            logger.exception(f"Getting available records by game {game_name}: {e}")
            raise
        
    async def get_in_transit_to_client_by_game(self, game_name: str) -> List[Record]:
        """
        Получение всех записей, которые едут к клиенту, определенной игры
        С группировкой по записям
        
        Args:
            game_name: название игры
        
        Return:
            Список Record
            
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.debug(f"Getting in transit client records by game: {game_name}")
        
        try:
            stmt = (
                select(Record)
                .join(Game, Record.game_id == Game.id)
                .where(
                    and_(
                        Record.status == RecordStatus.IN_TRANSIT_TO_CLIENT.value,
                        Game.name == game_name
                    )
                )
                .order_by(Record.id.asc())
            )
            result = await self.session.execute(stmt)
            records = result.scalars().all()
            
            logger.debug(f"Retrieved {len(records)} in transit client records")
            return records
        except Exception as e:
            logger.exception(f"Getting in transit client records by game {game_name}: {e}")
            raise
        
    async def get_in_transit_to_me_by_game(self, game_name: str) -> List[Record]:
        """
        Получение всех записей, которые едут к клиенту, определенной игры
        С группировкой по записям
        
        Args:
            game_name: название игры
        
        Return:
            Список Record
            
        Raises:
            Exception: При ошибке чтения
        """
        
        logger.debug(f"Getting in transit me records by game: {game_name}")
        
        try:
            stmt = (
                select(Record)
                .join(Game, Record.game_id == Game.id)
                .where(
                    and_(
                        Record.status == RecordStatus.IN_TRANSIT_TO_ME.value,
                        Game.name == game_name
                    )
                )
                .order_by(Record.id.asc())
            )
            result = await self.session.execute(stmt)
            records = result.scalars().all()
            
            logger.debug(f"Retrieved {len(records)} in transit me records")
            return records
        except Exception as e:
            logger.exception(f"Getting in transit me records by game {game_name}: {e}")
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
            
        Raises:
            Exception: При ошибке чтения
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
                            RecordStatus.IN_TRANSIT_TO_ME.value,
                            RecordStatus.IN_TRANSIT_TO_CLIENT
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
            logger.exception(f"Error getting expenses and incomes financials: {e}")
            raise
    
    async def get_sales_financials(self) -> Tuple[int, int]:
        """
        Получить выручку по играм и количество проданных дисков одним запросом.
        
        Выручка - грязная разница доходов и расходов по играм.
        
        Return:
            Кортеж (revenue, discs_count_sold)
            
        Raises:
            Exception: При ошибке чтения
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
                                RecordStatus.IN_TRANSIT_TO_CLIENT.value
                            ])
                        ), 
                        func.coalesce(Record.price_sold, 0) - func.coalesce(Record.price_purchase, 0)),
                        else_=0
                    )
                ), 0).label('revenue'),
                
                # Количество проданных дисков (только игры, без транзакций)
                func.count(
                    case(
                        (and_(
                            Record.status == RecordStatus.SOLD.value,
                            Record.game_id.isnot(None),
                            Record.util_id.is_(None)
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
            logger.exception(f"Error getting sales financials: {e}")
            raise
    
    async def get_in_transit_to_client_financial(self) -> Tuple[int, int]:
        """
        Получить сумму и количество записей, едущих к покупателю.
        
        Возвращает и сумму, и количество одним запросом,
        так как у них одинаковое условие фильтрации.
        
        Return:
            Кортеж (on_way, on_way_count)
            
        Raises:
            Exception: При ошибке чтения
        """
        logger.debug("Getting delivery to client (sum, count)")
        
        try:
            stmt = select(
                func.coalesce(func.sum(Record.price_sold), 0).label('on_way'),
                func.count(Record.id).label('on_way_count')
            ).where(
                and_(
                    Record.status == RecordStatus.IN_TRANSIT_TO_CLIENT.value,
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
            logger.exception(f"Error getting delivery to client: {e}")
            raise
    
    async def count_available_discs(self) -> int:
        """
        Подсчитать количество дисков в наличии.
        
        Return:
            Количество дисков со статусом 'Да'
            
        Raises:
            Exception: При ошибке чтения
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
            logger.exception(f"Error counting available discs: {e}")
            raise
    
    async def get_assets_value(self) -> Tuple[int, int]:
        """
        Получить стоимость товаров в наличии и 'едет ко мне' одним запросом.
        
        Берёт цену продажи, если она есть, иначе цену покупки.
        
        Return:
            Кортеж (available_sum, coming_to_me_sum)
        
        Raises:
            Exception: При ошибке чтения
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
                        (Record.status == RecordStatus.IN_TRANSIT_TO_ME.value, price),
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
            logger.exception(f"Error getting assets value: {e}")
            raise
    
    async def get_expenses_by_transaction(self, transaction_title: str) -> int:
        """
        Получить расходы по конкретной транзакции (например, Авито).
        
        Требует JOIN с таблицей utilities.
        
        Return:
            Сумма расходов по транзакции
        
        Raises:
            Exception: При ошибке чтения
        """
        logger.debug(f"Getting expenses for transaction '{transaction_title}'")
        
        try:
            stmt = select(
                func.coalesce(func.sum(Record.price_purchase), 0)
            ).join(
                Utility, Record.util_id == Utility.id
            ).where(
                Utility.title.ilike(f'%{transaction_title}%')
            )
            
            result = await self.session.execute(stmt)
            expenses = result.scalar()
            
            logger.debug(f"Expenses for '{transaction_title}': {expenses}")
            return expenses
            
        except Exception as e:
            logger.exception(f"Error getting expenses by transaction: {e}")
            raise