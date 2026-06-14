
from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
import sys
import os
from aiogram.utils.keyboard import InlineKeyboardBuilder
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from database import Database, db
import asyncio
from states.states import UserStates
from services.info_services import *
from services.notices_services import *
from services.records_services import *
from services.games_services import *
from services.bulk_orders_services import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder


MAIN_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="📒 ЗАПИСИ"),
            KeyboardButton(text="ℹ️ ИНФО"),
        ],
        [
            KeyboardButton(text="📦 ОПТ"),
            KeyboardButton(text="📝 ОПИСАНИЕ"),
        ],
        [
            KeyboardButton(text="📑 ТРАНЗАКЦИЯ"),
            KeyboardButton(text="⚙️ СЕРВИС"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_1_RECORDS_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="🔻 ПОКУПКА"),
            KeyboardButton(text="🔼 ПРОДАЖА"),
        ],
        [
            KeyboardButton(text="🔄 ОБМЕН"),
            KeyboardButton(text="🎫 БРОНЬ"),
        ],
        [
            KeyboardButton(text="✅ ЗАВЕРШЕН"),
            KeyboardButton(text="✅ ПОЛУЧЕН"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_1_INFO_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="📒 ЗАПИСИ"),
            KeyboardButton(text="💿 НАЛИЧИЕ"),
        ],
        [
            KeyboardButton(text="📦 ОПТ"),
            KeyboardButton(text="📊 ВСЕ ФИНАНСЫ"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_1_BULK_ORDER_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="🆕 СОЗДАТЬ ЗАКАЗ"),
        ],
        [
            KeyboardButton(text="🚚💰 ДОБАВИТЬ ДОСТАВКУ"),
        ],
        [
            KeyboardButton(text="✅ ЗАКАЗ ПОЛУЧЕН"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_1_NOTICE_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="🔹 БАЗОВОЕ"),
            KeyboardButton(text="🔑 ЧАСТНОЕ"),
        ],
        [
            KeyboardButton(text="🆕 ДЛЯ НОВЫХ"),
            KeyboardButton(text="♻️ ДЛЯ Б/У"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_1_SERVICE_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="📒 ЗАПИСИ"),
            KeyboardButton(text="📄 СПИСОК ИГР"),
        ],
        [
            KeyboardButton(text="📦 ОПТ"),
            KeyboardButton(text="📝 ОПИСАНИЕ"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_1_TRNS_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_2_INFO_RECORDS_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="🔢 ИНТЕРВАЛ"),
        ],
        [
            KeyboardButton(text="🚚👤 ЕДЕТ КО МНЕ"),
        ],
        [
           KeyboardButton(text="🚚👥 ЕДЕТ К ПОКУПАТЕЛЮ"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_2_INFO_BULK_ORDER_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="📦 ЗАКАЗ ПО ID"),
            KeyboardButton(text="🔢 ИНТЕРВАЛ ПО ID"),
        ],
        [
           KeyboardButton(text="🚚👤 ЕДЕТ КО МНЕ"),
           KeyboardButton(text="🗃️ ВСЕ ЗАКАЗЫ"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_2_INFO_ALL_FINANCED_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_2_INFO_AV_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="🔒 ДЛЯ МЕНЯ"),
            KeyboardButton(text="👥ДЛЯ КЛИЕНТА"),
        ],
        [
           KeyboardButton(text="🆔 ПО ЗАПИСЯМ"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_2_SERVICE_RECORDS_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="🔧 ИЗМЕНИТЬ СТРОКУ ПО ID"),
        ],
        [
           KeyboardButton(text="❌ УДАЛИТЬ СТРОКУ ПО ID"),
        ],
        [
           KeyboardButton(text="🛠️ УСТАНОВИТЬ ЦЕНУ ОПРЕДЕЛЕННЫМ ИГРАМ"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_2_SERVICE_NOTICE_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="🔧 ИЗМЕНИТЬ ЧАСТНЫЙ ТЭГ"),
        ],
        [
           KeyboardButton(text="🔧 ИЗМЕНИТЬ БАЗУ"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_2_SERVICE_GAMES_LIST_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        # Первый ряд кнопок
        [
            KeyboardButton(text="❌ УДАЛИТЬ ИГРУ ИЗ СПИСКА"),
        ],
        [
           KeyboardButton(text="🆕 ДОБАВИТЬ ИГРУ В СПИСОК"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)

LVL_2_SERVICE_BULK_ORDER_REPLY_KB = ReplyKeyboardMarkup(
    keyboard=[
        [
           KeyboardButton(text="❌ УДАЛИТЬ ЗАКАЗ ПО ID"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,  # Адаптирует размер кнопок под экран
    one_time_keyboard=False,  # Не скрывать после нажатия
    input_field_placeholder="Выберите действие...",  # Текст в поле ввода
    selective=False  # Показывать всем или только упомянутым (True/False)
)


