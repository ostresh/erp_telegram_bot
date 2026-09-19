from dataclasses import asdict

from app.service.finance.schemas import FinanceReport
from app.bot.utils.emoji import Emoji
from app.db.models import Record
from app.db.statuses import RecordStatus
from app.bot.messages.menu import MenuConstants


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
            record: объект Record
            
        Returns:
            HTML строка для вывода в telegram
        """
        
        money = MessageFormatter.format_money
        
        record_id = f"{Emoji.ID} <b>{record.id}</b>" if record.id is not None else ''
        
        purchase_at = (
            f" • {Emoji.DATE} {record.purchase_at.strftime('%d.%m.%Y')}"
            if record.purchase_at is not None
            else ''
        )
        sold_at = (
            f" • {Emoji.DATE} {record.sold_at.strftime('%d.%m.%Y')}"
            if record.sold_at is not None
            else ''
        )
        
        game = (
            f"{Emoji.GAME} <b>{record.game.name if record.game else f'ID:{record.game_id}'}</b>"
            if record.game_id is not None
            else ''
        )
        trns = (
            f"{Emoji.TRNS} <b>{record.utility.title if record.utility else f'ID:{record.trns_id}'}</b>"
            if record.trns_id is not None
            else ''
        )
        
        price_buy = (
            f"{Emoji.PRICE_BUY} <code>{money(record.price_purchase)}</code>р."
            if record.price_purchase is not None
            else f"{Emoji.PRICE_BUY} 0р."
        )
        
        price_sell = (
            f" • {Emoji.PRICE_SELL} <code>{money(record.price_selling)}</code>р."
            if record.price_selling is not None
            else f" • {Emoji.PRICE_SELL} 0р."
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
            f"{game} {trns}",
            f"{price_buy}{price_sell}",
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
    def format_row_record(record: Record) -> str:
        """
        Полное форматирование записи в текстовое сообщение.
        
        Выводит все поля записи в человекочитаемом виде
        
        Args:
            record - объект записи (с загруженными связями game и utility)
            
        Return:
            Строка с полной информацией о записи
        """
        
        purchase_date = (
            record.purchase_at.strftime("%d.%m.%Y") 
            if record.purchase_at else ''
        )
        sold_date = (
            record.sold_at.strftime("%d.%m.%Y") 
            if record.sold_at else ''
        )
        
        # Связанные объекты (могут быть None)
        game_name = record.game.name if record.game else ''
        utility_title = record.utility.title if record.utility else ''
        
        lines = [
            f"ID: {record.id}",
            f"Дата покупки: {purchase_date}",
            f"Дата продажи: {sold_date}",
            f"Игра: {game_name}",
            f"Транзакция: {utility_title}",
            f"Оптовый заказ: {record.bulk_order_id or ''}",
            f"Цена покупки: {record.price_purchase or 0}",
            f"Цена продажи: {record.price_selling or 0}",
            f"Цена продано: {record.price_sold or 0}",
            f"Статус: {record.status or ''}",
            f"Обмен: {record.swap or ''}",
            f"Бронь: {record.reserve or ''}",
            f"Комментарий: {record.comment or ''}",
        ]
        
        return '\n'.join(lines)