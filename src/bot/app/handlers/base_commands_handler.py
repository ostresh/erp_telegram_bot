from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import sys
import os
import subprocess
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database import db
import asyncio
from services.menu_services import *
from aiogram.fsm.context import FSMContext
from src.bot.app.keyboards.inline_keyboards import *
from src.bot.app.keyboards.reply_keyboards import *
from src.bot.app.messages.menu_messages import *
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start - вызов главного меню"""
    menu = await create_menu('main')
    await message.answer(text = menu['text'],
    reply_markup=menu['kb'],
    parse_mode='HTML'
)

@router.message(Command("test_db"))
async def cmd_test_db(message: Message):
    """Проверка подключения к базе данных"""
    status = await db.test_connection()
    await message.answer(status)
    
    
@router.message(Command("restart"))
async def restart_bot(message: Message):
    '''Команда перезапуска бота при сбое сервера'''
    
    await message.answer("⏳ Бот перезагружается. Подождите 5 секунд...")
    
    # 1. Ждем 5 секунд. В это время бот всё еще работает в ЭТОМ ЖЕ окне.
    await asyncio.sleep(5)
    
    
    os.execv(sys.executable, [sys.executable] + sys.argv)
    
    