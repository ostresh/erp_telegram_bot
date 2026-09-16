from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.db.status.status import RecordStatus


class Base(DeclarativeBase):
    pass


class Game(Base):
    """Модель названия игр"""
    __tablename__ = 'games_list'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)

    records: Mapped[List["Record"]] = relationship(back_populates="game")

    def __repr__(self) -> str:
        return f"<Game(id={self.id}, name='{self.name}')>"


class Utility(Base):
    """Модель утилит/транзакций"""
    __tablename__ = 'utils_list'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    records: Mapped[List["Record"]] = relationship(back_populates="utility")

    def __repr__(self) -> str:
        return f"<Utility(id={self.id}, title='{self.title}')>"

class Description(Base):
    """Модель для описания"""
    __tablename__ = 'description'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text)
    
    def __repr__(self):
        return f"<Description(id={self.id}, title='{self.title}')>"
    

class Record(Base):
    """Модель записи (основная таблица)"""
    __tablename__ = 'record'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

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

    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    swap: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    reserve: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    game: Mapped[Optional["Game"]] = relationship(back_populates="records")
    utility: Mapped[Optional["Utility"]] = relationship(back_populates="records")
    bulk_order: Mapped[Optional["BulkOrder"]] = relationship(back_populates="records")

    __table_args__ = (
        CheckConstraint(
            "(game_id IS NOT NULL AND trns_id IS NULL) OR (game_id IS NULL AND trns_id IS NOT NULL)",
            name="check_game_or_util"
        ),
    )

    @property
    def is_available(self) -> bool:
        """Проверяет доступна ли запись для продажи"""
        return self.status == RecordStatus.AVAILABLE.value

    @property
    def profit(self) -> Optional[int]:
        """Вычисляет прибыль"""
        if self.price_sold is not None and self.price_purchase is not None:
            return self.price_sold - self.price_purchase
        return None

    def __repr__(self) -> str:
        return f"<Record(id={self.id})>"


class BulkOrder(Base):
    """Модель оптового заказа"""
    __tablename__ = 'bulk_order'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

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