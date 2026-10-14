from dataclasses import asdict
from typing import List, Tuple
from zoneinfo import ZoneInfo

from app.core.db.statuses.bulk_order import BulkOrderStatus
from app.core.dto import AvailableGameDTO
from app.core.service.finance.schemas import FinanceReport
from app.interfaces.bot.utils.emoji import Emoji
from app.core.db.models import BulkOrder, Game, Record
from app.core.db.statuses import RecordStatus
from app.interfaces.bot.messages.menu import MenuConstants


class MessageFormatter:
    """Форматирование данных в HTML для Telegram"""
    
    @staticmethod
    def format_money(amount: int) -> str:
        """
        Форматирование чисел
        
        Пример: 12345 → '12.345'
        
        Args:
            amount - сумма в рублях
            
        Return:
            Отформатированная строка
        """
        return f"{amount:,}".replace(',', '.')
    
    @staticmethod
    def format_finance_report(
        report: FinanceReport, 
        fields: list[str] | None = None
    ) -> str:
        """
        Форматирование финансового отчёта в HTML.
        
        Универсальная функция: выводит только те поля,
        которые указаны в fields (или все, если fields=None).
        Если поле отсутствует или пустое — строка не выводится.
        
        Args:
            report - финансовый отчёт
            fields - список полей для вывода (ключи FinanceReport)
            
        Return:
            HTML-строка с отчётом
        """
        data = asdict(report)
        money = MessageFormatter.format_money
        
        formatters = {
            'expenses':       lambda v: f"{Emoji.EXPENSES} <strong>РАСХОДЫ</strong> • <code>{money(v)}</code>р.\n",
            'incomes':        lambda v: f"{Emoji.INCOMES} <strong>ДОХОДЫ</strong> • <code>{money(v)}</code>р.\n",
            'revenue':        lambda v: f"{Emoji.REVENUE} <strong>ВЫРУЧКА</strong> • <code>{money(v)}</code>р.\n",
            'net_profit':     lambda v: f"{Emoji.NET_PROFIT} <strong>ЧИСТАЯ ПРИБЫЛЬ</strong> • <code>{money(v)}</code>р.\n",
            'avito_expenses': lambda v: f"{Emoji.AVITO} <strong>РАСХОДЫ АВИТО</strong> • <code>{money(v)}</code>р.\n",
            'discs_count_sold': lambda v: f"{Emoji.DISCS_COUNT} <strong>ДИСКОВ ПРОДАНО</strong> • <code>{v}</code>\n",
            'avg_revenue':    lambda v: f"{Emoji.AVG_REVENUE} <strong>СРЕДНЯЯ ВЫРУЧКА</strong> • <code>{money(v)}</code>р.\n",
            'on_account':     lambda v: f"{Emoji.ON_ACCOUNT} <strong>НА СЧЕТУ</strong> • <code>{money(v)}</code>р.\n",
            'discs_count':    lambda v: f"{Emoji.DISCS_COUNT} <strong>ДИСКОВ В НАЛИЧИИ</strong> • <code>{v}</code>\n",
            'on_way':         lambda v: f"{Emoji.ON_WAY} <strong>ЕДЕТ К ПОКУПАТЕЛЮ</strong> • <code>{money(v)}</code>р.\n",
            'on_way_count':   lambda v: f"{Emoji.ON_WAY} <strong>ЕДЕТ К ПОКУПАТЕЛЮ (ШТ.)</strong> • <code>{v}</code>\n",
            'all_assets':     lambda v: f"{Emoji.ALL_ASSETS} <strong>ВСЕ АКТИВЫ</strong> • <code>{money(v)}</code>р.\n",
        }
        
        # Если поля не указаны — выводим все
        if fields is None:
            fields = list(formatters.keys())
        
        result = ''
        for field in fields:
            value = data.get(field)
            if value and field in formatters:
                result += formatters[field](value)
        
        return result.strip()
    
    @staticmethod
    def format_record(record: Record) -> str:
        """
        Форматирует один объект Record для вывода в Telegram.
        
        Args:
            record: объект Record с relations
            
        Returns:
            HTML строка для вывода в telegram
        """
        
        money = MessageFormatter.format_money
        
        record_id = f"{Emoji.ID} <b>{record.id}</b>" if record.id is not None else ''
        
        purchase_at = (
            f" • {Emoji.DATE} {record.purchase_at.astimezone(ZoneInfo('Europe/Moscow')).strftime('%d.%m.%Y')}"
            if record.purchase_at is not None
            else ''
        )
        sold_at = (
            f" • {Emoji.DATE} {record.sold_at.astimezone(ZoneInfo('Europe/Moscow')).strftime('%d.%m.%Y')}"
            if record.sold_at is not None
            else ''
        )
        
        game = (
            f"{Emoji.GAME} <b>{record.game.name if record.game else f'ID:{record.game_id}'}</b>"
            if record.game_id is not None
            else ''
        )
        trns = (
            f"{Emoji.TRNS} <b>{record.utility.title if record.utility else f'ID:{record.util_id}'}</b>"
            if record.util_id is not None
            else ''
        )
        
        price_purchase = (
            f"{Emoji.PRICE_PURCHASE} <code>{money(record.price_purchase)}</code>р."
            if record.price_purchase is not None
            else f"{Emoji.PRICE_PURCHASE} 0р."
        )
        
        price_selling = (
            f" • {Emoji.PRICE_SELLING} <code>{money(record.price_selling)}</code>р."
            if record.price_selling is not None
            else f" • {Emoji.PRICE_SELLING} 0р."
        )
        
        price_sold = (
            f"{Emoji.PRICE_SOLD} <code>{money(record.price_sold)}</code>р."
            if record.price_sold is not None
            else f"{Emoji.PRICE_SOLD} 0р."
        )
        
        profit = (
            f" • {Emoji.REVENUE} <code>{money(record.profit)}</code>р."
            if record.profit is not None
            else f" • {Emoji.REVENUE} 0р."
        )
        
        status = RecordStatus(record.status)
        status_text = f"{Emoji.STATUS} <b>{status.display_name}</b>"
        
        swap = f"{Emoji.SWAP} <b>{record.swap}</b>" if record.swap else ''
        reserve = f"{Emoji.RESERVE} <b>{record.reserve}</b>" if record.reserve else ''
        comment = f"{Emoji.COMMENT} <b>{record.comment}</b>" if record.comment else ''
        
        lines = [
            f"{record_id}{purchase_at}{sold_at}",
            f"{game}",
            f"{trns}",
            f"{price_purchase}{price_selling}",
            f"{price_sold}{profit}",
            status_text,
            swap,
            reserve,
            comment,
        ]
        
        formatted = '\n'.join(filter(None, lines))
        
        formatted += MenuConstants.HORIZONTAL_LINE
        
        return formatted
    
    @staticmethod
    def format_many_records(
        records: List[Record],
        chunk_size: int = 7,
    ) -> List[str]:
        """
        Форматирует несколько объектов Record для вывода в Telegram частями.

        Разбивает список записей на чанки по chunk_size элементов
        и форматирует каждый чанк в отдельную HTML-строку.

        Используется для вывода больших списков записей несколькими
        сообщениями, чтобы не превысить лимит Telegram на длину
        сообщения (4096 символов).

        Args:
            records: список объектов Record с relations
            chunk_size: количество объектов Record в одном сообщении

        Returns:
            List[str]: список HTML-строк для вывода в Telegram.
                    Каждая строка содержит до chunk_size записей
                    (последняя может содержать меньше)

        Raises:
            ValueError: если chunk_size меньше 1
        """
        if chunk_size < 1:
            raise ValueError(f"chunk_size должен быть >= 1, получено {chunk_size}")

        if not records:
            return []

        chunks = []

        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]
            formatted_chunk = ''.join(
                MessageFormatter.format_record(record) for record in chunk
            )
            chunks.append(formatted_chunk)

        return chunks
        
    
    @staticmethod
    def format_available_game(game_dto: AvailableGameDTO) -> str:
        """
        Форматирует один Game для вывода в Telegram.
        
        Args:
            game_dto: объект Record с relations
            
        Returns:
            HTML строка для вывода в telegram
        """
        
        money = MessageFormatter.format_money
        
        game_name = f"{Emoji.GAME} <b>{game_dto.game.name}</b>" if game_dto.game is not None else ''
        
        price_purchase = (
            f"{Emoji.PRICE_PURCHASE} <code>{money(game_dto.price_purchase)}</code>р."
            if game_dto.price_purchase is not None
            else f"{Emoji.PRICE_PURCHASE} 0р."
        )
        
        price_selling = (
            f" • {Emoji.PRICE_SELLING} <code>{money(game_dto.price_selling)}</code>р."
            if game_dto.price_selling is not None
            else f" • {Emoji.PRICE_SELLING} 0р."
        )
        
        games_count = (
            f" • {Emoji.DISCS_COUNT} <code>{game_dto.games_count}</code> шт."
            if game_dto.games_count is not None
            else f" • {Emoji.DISCS_COUNT} 0 шт."
        )
        
        lines = [
            f"{game_name}",
            f"{price_purchase}{price_selling}{games_count}",
        ]
        
        formatted = '\n'.join(filter(None, lines))
        
        formatted += MenuConstants.HORIZONTAL_LINE
        
        return formatted
    
    @staticmethod
    def format_many_available_games(
        game_dtos: List[AvailableGameDTO],
        chunk_size: int = 15,
    ) -> List[str]:
        """
        Форматирует несколько объектов Record для вывода в Telegram частями.

        Разбивает список записей на чанки по chunk_size элементов
        и форматирует каждый чанк в отдельную HTML-строку.

        Используется для вывода больших списков записей несколькими
        сообщениями, чтобы не превысить лимит Telegram на длину
        сообщения (4096 символов).

        Args:
            records: список объектов Record с relations
            chunk_size: количество объектов Record в одном сообщении

        Returns:
            List[str]: список HTML-строк для вывода в Telegram.
                    Каждая строка содержит до chunk_size записей
                    (последняя может содержать меньше)

        Raises:
            ValueError: если chunk_size меньше 1
        """
        if chunk_size < 1:
            raise ValueError(f"chunk_size должен быть >= 1, получено {chunk_size}")

        if not game_dtos:
            return []

        chunks = []

        for i in range(0, len(game_dtos), chunk_size):
            chunk = game_dtos[i:i + chunk_size]
            formatted_chunk = ''.join(
                MessageFormatter.format_available_game(game) for game in chunk
            )
            chunks.append(formatted_chunk)

        return chunks
       
    @staticmethod
    def format_bulk_order(bulk_order: BulkOrder) -> str:
        """
        Форматирует один объект BulkOrder для вывода в Telegram.

        Args:
            bulk_order: объект BulkOrder

        Returns:
            HTML строка для вывода в telegram
        """

        money = MessageFormatter.format_money

        order_id = f"{Emoji.ID} <b>{bulk_order.id}</b>" if bulk_order.id is not None else ''

        created_at = (
            f" • {Emoji.DATE} {bulk_order.created_at.astimezone(ZoneInfo('Europe/Moscow')).strftime('%d.%m.%Y')}"
            if bulk_order.created_at is not None
            else ''
        )
        arrived_at = (
            f" • {Emoji.DATE} {bulk_order.arrived_at.astimezone(ZoneInfo('Europe/Moscow')).strftime('%d.%m.%Y')}"
            if bulk_order.arrived_at is not None
            else ''
        )
        record_ids = (
            f"{Emoji.RECORDS} {bulk_order.record_ids[0]} - {bulk_order.record_ids[-1]}"
            if bulk_order.record_ids is not None
            else ''
        )
        
        seller = (
            f"{Emoji.SELLER} <b>{bulk_order.seller}</b>"
            if bulk_order.seller
            else ''
        )

        total_count = (
            f"{Emoji.DISCS_COUNT} <code>{bulk_order.total_count}</code> шт."
            if bulk_order.total_count is not None
            else f"{Emoji.DISCS_COUNT} 0 шт."
        )

        total_cost = (
            f" • {Emoji.BULK_ORDER_COST} <code>{money(bulk_order.total_cost)}</code>р."
            if bulk_order.total_cost is not None
            else f" • {Emoji.BULK_ORDER_COST} 0р."
        )

        delivery_cost = (
            f"{Emoji.BULK_ORDER_DELIVERY_COST} <code>{money(bulk_order.delivery_cost)}</code>р."
            if bulk_order.delivery_cost is not None
            else f"{Emoji.BULK_ORDER_DELIVERY_COST} 0р."
        )

        status_text = ''
        if bulk_order.order_status:
            status = BulkOrderStatus(bulk_order.order_status)
            status_text = f"{Emoji.STATUS} <b>{status.display_name}</b>"

        lines = [
            f"{order_id}{created_at}{arrived_at}",
            record_ids,
            seller,
            f"{total_count}{total_cost}",
            delivery_cost,
            status_text,
        ]

        formatted = '\n'.join(filter(None, lines))

        formatted += MenuConstants.HORIZONTAL_LINE

        return formatted

    @staticmethod
    def format_many_bulk_orders(
        bulk_orders: List[BulkOrder],
        chunk_size: int = 7,
    ) -> List[str]:
        """
        Форматирует несколько объектов BulkOrder для вывода в Telegram частями.

        Разбивает список оптовых заказов на чанки по chunk_size элементов
        и форматирует каждый чанк в отдельную HTML-строку.

        Используется для вывода больших списков заказов несколькими
        сообщениями, чтобы не превысить лимит Telegram на длину
        сообщения (4096 символов).

        Args:
            bulk_orders: список объектов BulkOrder
            chunk_size: количество объектов BulkOrder в одном сообщении

        Returns:
            List[str]: список HTML-строк для вывода в Telegram.
                    Каждая строка содержит до chunk_size заказов
                    (последняя может содержать меньше)

        Raises:
            ValueError: если chunk_size меньше 1
        """
        if chunk_size < 1:
            raise ValueError(f"chunk_size должен быть >= 1, получено {chunk_size}")

        if not bulk_orders:
            return []

        chunks = []

        for i in range(0, len(bulk_orders), chunk_size):
            chunk = bulk_orders[i:i + chunk_size]
            formatted_chunk = ''.join(
                MessageFormatter.format_bulk_order(order)
                for order in chunk
            )
            chunks.append(formatted_chunk)

        return chunks