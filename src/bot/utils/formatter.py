from bot.service.finance.schemas import FinanceReport
from bot.utils.emoji import Emoji
from bot.db.models import Record

from dataclasses import asdict


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
            'expenses':       lambda v: f"\n{Emoji.EXPENSES} <strong>РАСХОДЫ</strong> • <code>{money(v)}</code>р.\n",
            'incomes':        lambda v: f"\n{Emoji.INCOMES} <strong>ДОХОДЫ</strong> • <code>{money(v)}</code>р.\n",
            'revenue':        lambda v: f"\n{Emoji.REVENUE} <strong>ВЫРУЧКА</strong> • <code>{money(v)}</code>р.\n",
            'net_profit':     lambda v: f"\n{Emoji.NET_PROFIT} <strong>ЧИСТАЯ ПРИБЫЛЬ</strong> • <code>{money(v)}</code>р.\n",
            'avito_expenses': lambda v: f"\n{Emoji.AVITO} <strong>РАСХОДЫ АВИТО</strong> • <code>{money(v)}</code>р.\n",
            'discs_count_sold': lambda v: f"\n{Emoji.DISCS_COUNT} <strong>ДИСКОВ ПРОДАНО</strong> • <code>{v}</code>\n",
            'avg_revenue':    lambda v: f"\n{Emoji.AVG_REVENUE} <strong>СРЕДНЯЯ ВЫРУЧКА</strong> • <code>{money(v)}</code>р.\n",
            'on_account':     lambda v: f"\n{Emoji.ON_ACCOUNT} <strong>НА СЧЕТУ</strong> • <code>{money(v)}</code>р.\n",
            'discs_count':    lambda v: f"\n{Emoji.DISCS_COUNT} <strong>ДИСКОВ В НАЛИЧИИ</strong> • <code>{v}</code>\n",
            'on_way':         lambda v: f"\n{Emoji.ON_WAY} <strong>ЕДЕТ К ПОКУПАТЕЛЮ</strong> • <code>{money(v)}</code>р.\n",
            'on_way_count':   lambda v: f"\n{Emoji.ON_WAY} <strong>ЕДЕТ К ПОКУПАТЕЛЮ (ШТ.)</strong> • <code>{v}</code>\n",
            'all_assets':     lambda v: f"\n{Emoji.ALL_ASSETS} <strong>ВСЕ АКТИВЫ</strong> • <code>{money(v)}</code>р.\n",
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