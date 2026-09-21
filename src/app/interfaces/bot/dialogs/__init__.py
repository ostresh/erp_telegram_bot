"""
Регистрация всех диалогов в проекте.
"""

from aiogram import Dispatcher

from app.interfaces.bot.dialogs.test.hello_dialog import hello_dialog
from app.interfaces.bot.dialogs.actions.goods.buy_goods.dialog import buy_goods_dialog
from app.interfaces.bot.dialogs.actions.goods.sell_goods.dialog import sell_goods_dialog

def register_dialogs(dp: Dispatcher) -> None:
    """Регистрирует все диалоги в диспетчере."""
    dp.include_router(hello_dialog)
    dp.include_router(buy_goods_dialog)
    dp.include_router(sell_goods_dialog)