from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, validates

from app.db.statuses import RecordStatus


class Base(DeclarativeBase):
    pass


class Game(Base):
    """
    Модель названия игр.
    
    Хранит уникальные названия игр, которые могут быть связаны с записями.
    
    Attributes:
        id (int, auto): Уникальный идентификатор
        name (str, required): Название игры, уникальное
    
    Relationships:
        records (List[Record]): Записи, связанные с этой игрой
    """
    
    __tablename__ = 'games_list'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)

    records: Mapped[List["Record"]] = relationship(back_populates="game")

    def __repr__(self) -> str:
        return f"<Game(id={self.id}, name='{self.name}')>"


class Utility(Base):
    """
    Модель утилит/транзакций.
    
    Хранит типы транзакций (например, "Авито", "Юла", "ВКонтакте"),
    через которые были совершены покупки или продажи.
    
    Attributes:
        id (int, auto): Уникальный идентификатор
        title (str, required): Название транзакции, уникальное
    
    Relationships:
        records (List[Record]): Записи, связанные с этой транзакцией
    """
    
    __tablename__ = 'utils_list'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    records: Mapped[List["Record"]] = relationship(back_populates="utility")

    def __repr__(self) -> str:
        return f"<Utility(id={self.id}, title='{self.title}')>"

class Description(Base):
    """
    Модель для текстовых описаний.
    
    Хранит текстовые описания для различных целей.
    
    Attributes:
        id (int, auto): Уникальный идентификатор
        title (str, required): Текст описания
    """
    
    __tablename__ = 'description'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text)
    
    def __repr__(self):
        return f"<Description(id={self.id}, title='{self.title}')>"
    

class Record(Base):
    """
    Модель записи (товара).
    
    Хранит информацию о каждой покупке/продаже товара.
    Запись должна быть либо игрой (game_id), либо утилитой (trns_id),
    но не обоими одновременно.
    
    Attributes:
        id (int, auto): Уникальный идентификатор
        game_id (int, required): ID игры, если не указана утилита
        trns_id (int, required): ID транзакции, если не указана игра
        bulk_order_id (int): ID оптового заказа
        purchase_at (datetime, auto): Дата покупки
        sold_at (datetime): Дата продажи
        price_purchase (int): Цена покупки
        price_selling (int): Цена продажи (желаемая)
        price_sold (int): Цена фактической продажи
        status (str, auto): Статус записи, default 'available'
        swap (str): Обмен
        reserve (str): Резерв
        comment (str): Комментарий
    
    Relationships:
        game (Game): Игра, связанная с записью
        utility (Utility): Транзакция, связанная с записью
        bulk_order (BulkOrder): Оптовый заказ, связанный с записью
    
    Properties:
        is_available (bool): Доступна ли запись для продажи
        profit (int): Прибыль от продажи (если продано)
    """
    
    __tablename__ = 'record'

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        autoincrement=True
        )

    purchase_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(timezone.utc)
    )
    sold_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    game_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("games_list.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    trns_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("utils_list.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    bulk_order_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("bulk_order.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    price_purchase: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_selling: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_sold: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    status: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    swap: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    reserve: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    game: Mapped[Optional["Game"]] = relationship(back_populates="records")
    utility: Mapped[Optional["Utility"]] = relationship(back_populates="records")
    bulk_order: Mapped[Optional["BulkOrder"]] = relationship(back_populates="records")

    @validates('game_id', 'trns_id')
    def validate_game_or_util(self, key, value):
        """Проверка: либо игра, либо утилита"""
        return value
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Валидация при создании
        if self.game_id is None and self.trns_id is None:
            raise ValueError("Record должен быть либо игрой, либо утилитой")
        if self.game_id is not None and self.trns_id is not None:
            raise ValueError("Record не может быть одновременно игрой и утилитой")

    @property
    def is_available(self) -> bool:
        """Проверяет доступна ли запись для продажи"""
        return self.status == RecordStatus.AVAILABLE.value

    @property
    def profit(self) -> Optional[int]:
        """Вычисляет прибыль"""
        if self.price_sold is not None and self.price_purchase is not None:
            return self.price_sold - self.price_purchase
        elif self.price_sold is not None and self.price_purchase is None:
            return self.price_sold
        elif self.price_sold is None and self.price_purchase is not None:
            return 0 - self.price_purchase
        return None

    def __repr__(self) -> str:
        return f"<Record(id={self.id})>"


class BulkOrder(Base):
    """
    Модель оптового заказа.
    
    Хранит информацию о оптовых закупках товаров.
    Один оптовый заказ может содержать множество записей.
    
    Attributes:
        id (int, auto): Уникальный идентификатор
        seller (str): Имя продавца
        order_status (str, auto): Статус заказа, default 'created'
        total_count (int): Общее количество товаров
        total_cost (int): Общая стоимость заказа
        delivery_cost (int): Стоимость доставки
        created_at (datetime, auto): Дата создания
        arrived_at (datetime): Дата прибытия
    
    Relationships:
        records (List[Record]): Записи, связанные с этим заказом
    
    Properties:
        record_ids (List[int]): Список ID записей заказа
        is_arrived (bool): Прибыл ли заказ
    """
    
    __tablename__ = 'bulk_order'

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
        autoincrement=True
        )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    arrived_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    seller: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    order_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    total_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_cost: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    delivery_cost: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    records: Mapped[List["Record"]] = relationship(back_populates="bulk_order")

    @property
    def record_ids(self) -> List[int]:
        """Возвращает список ID записей"""
        return [r.id for r in self.records]

    @property
    def is_arrived(self) -> bool:
        """Проверяет, прибыл ли заказ"""
        return self.arrived_at is not None

    def __repr__(self) -> str:
        return f"<BulkOrder(id={self.id}, seller='{self.seller}', status='{self.order_status}')>"
    
    
class MessageToDelete(Base):
    """
    Сообщения бота, запланированные к удалению.
    
    Хранит информацию о сообщениях-результатах, которые должны быть удалены через определённое время.
    Используется для поддержания чистоты чата.
    
    Attributes:
        id (int, auto): Уникальный идентификатор
        chat_id (int, required): ID чата, где находится сообщение
        message_id (int, required): ID сообщения бота
        user_id (int, required): ID пользователя, для которого показано сообщение
        created_at (datetime, auto): Дата планирования удаления
    """
    
    __tablename__ = 'message_to_delete'
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    
    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True,
        nullable=False
    )
    
    message_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True,
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return (
            f"<MessageToDelete(id={self.id}, chat_id={self.chat_id}, "
            f"message_id={self.message_id}, user_id={self.user_id})>"
        )