from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from database import Database, db
import asyncio

router = Router()

@router.inline_query(F.query.startswith("@aviable "))
async def inline_search(inline_query: InlineQuery):
    """
    Обрабатывает инлайн-запросы: выводит названия игр в наличии
    Вызывается когда пользователь вводит @username_бота @aviable текст
    """
    
    query = inline_query.query.replace('@aviable ', '').strip()
    
    if not query:
        # Если запрос пустой, показываем подсказку
        await inline_query.answer(
            results=[],
            switch_pm_text="Начните вводить текст для поиска",
            switch_pm_parameter="start",
            cache_time=300
        )
        return
    
    # Поиск в БД по запросу
    results = await db.fetch(f"SELECT games_list.name FROM games_list JOIN records ON records.game_id = games_list.id WHERE games_list.name ILIKE $1 AND records.status = 'Да' GROUP BY games_list.name ORDER BY games_list.name", f'%{query}%')
    
    # Преобразуем результаты в формат для Telegram
    inline_results = []
    
    for i, item in enumerate(results[:50]):  # Telegram ограничивает 50 результатов
        inline_results.append(
            InlineQueryResultArticle(
                id=str(i),  # ОБЯЗАТЕЛЬНО! Уникальный ID для каждого результата
                title=item.get('name'),
                input_message_content=InputTextMessageContent(  # ОБЯЗАТЕЛЬНО!
                    message_text=(
                        f"<code>{item.get('name')}</code>\n"
                    ),
                    parse_mode='HTML',
                    disable_web_page_preview=True
                ),
            )
        )
    
    await inline_query.answer(
        results=inline_results,
        cache_time=1,  # Кэшировать на 1 секунду
        is_personal=True  # Результаты персональные
    )


@router.inline_query(F.query.startswith("@delivery_to_me"))
async def inline_search(inline_query: InlineQuery):
    """
    Обрабатывает инлайн-запросы: выводит названия игр в наличии
    Вызывается когда пользователь вводит @username_бота @aviable текст
    """
    
    query = inline_query.query.replace('@delivery_to_me ', '').strip()
    
    if not query:
        # Если запрос пустой, показываем подсказку
        await inline_query.answer(
            results=[],
            switch_pm_text="Начните вводить текст для поиска",
            switch_pm_parameter="start",
            cache_time=300
        )
        return
    
    # Поиск в БД по запросу
    results = await db.fetch(f"SELECT games_list.name FROM games_list JOIN records ON records.game_id = games_list.id WHERE games_list.name ILIKE $1 AND records.status = 'Едет ко мне' AND COALESCE(comment, '') NOT ILIKE '%Оптовый заказ%' GROUP BY games_list.name ORDER BY games_list.name", f'%{query}%')
    
    # Преобразуем результаты в формат для Telegram
    inline_results = []
    
    for i, item in enumerate(results[:50]):  # Telegram ограничивает 50 результатов
        inline_results.append(
            InlineQueryResultArticle(
                id=str(i),  # ОБЯЗАТЕЛЬНО! Уникальный ID для каждого результата
                title=item.get('name'),
                input_message_content=InputTextMessageContent(  # ОБЯЗАТЕЛЬНО!
                    message_text=(
                        f"<code>{item.get('name')}</code>\n"
                    ),
                    parse_mode='HTML',
                    disable_web_page_preview=True
                ),
            )
        )
    
    await inline_query.answer(
        results=inline_results,
        cache_time=1,  # Кэшировать на 1 секунду
        is_personal=True  # Результаты персональные
    )


@router.inline_query(F.query.startswith("@delivery_to_client"))
async def inline_search(inline_query: InlineQuery):
    """
    Обрабатывает инлайн-запросы: выводит названия игр в наличии
    Вызывается когда пользователь вводит @username_бота @aviable текст
    """
    
    query = inline_query.query.replace('@delivery_to_client ', '').strip()
    
    if not query:
        # Если запрос пустой, показываем подсказку
        await inline_query.answer(
            results=[],
            switch_pm_text="Начните вводить текст для поиска",
            switch_pm_parameter="start",
            cache_time=300
        )
        return
    
    # Поиск в БД по запросу
    results = await db.fetch(f"SELECT games_list.name FROM games_list JOIN records ON records.game_id = games_list.id WHERE games_list.name ILIKE $1 AND records.status = 'Едет к покупателю' GROUP BY games_list.name ORDER BY games_list.name", f'%{query}%')
    
    # Преобразуем результаты в формат для Telegram
    inline_results = []
    
    for i, item in enumerate(results[:50]):  # Telegram ограничивает 50 результатов
        inline_results.append(
            InlineQueryResultArticle(
                id=str(i),  # ОБЯЗАТЕЛЬНО! Уникальный ID для каждого результата
                title=item.get('name'),
                input_message_content=InputTextMessageContent(  # ОБЯЗАТЕЛЬНО!
                    message_text=(
                        f"<code>{item.get('name')}</code>\n"
                    ),
                    parse_mode='HTML',
                    disable_web_page_preview=True
                ),
            )
        )
    
    await inline_query.answer(
        results=inline_results,
        cache_time=1,  # Кэшировать на 1 секунду
        is_personal=True  # Результаты персональные
    )


@router.inline_query(F.query.startswith("@reserve"))
async def inline_search(inline_query: InlineQuery):
    """
    Обрабатывает инлайн-запросы: выводит названия игр в наличии
    Вызывается когда пользователь вводит @username_бота @aviable текст
    """
    
    query = inline_query.query.replace('@reserve ', '').strip()
    
    if not query:
        # Если запрос пустой, показываем подсказку
        await inline_query.answer(
            results=[],
            switch_pm_text="Начните вводить текст для поиска",
            switch_pm_parameter="start",
            cache_time=300
        )
        return
    
    # Поиск в БД по запросу
    results = await db.fetch(f"SELECT games_list.name FROM games_list JOIN records ON records.game_id = games_list.id WHERE games_list.name ILIKE $1 AND (records.status = 'Едет ко мне' OR records.status = 'Да') AND reserve IS NULL GROUP BY games_list.name ORDER BY games_list.name", f'%{query}%')
    
    # Преобразуем результаты в формат для Telegram
    inline_results = []
    
    for i, item in enumerate(results[:50]):  # Telegram ограничивает 50 результатов
        inline_results.append(
            InlineQueryResultArticle(
                id=str(i),  # ОБЯЗАТЕЛЬНО! Уникальный ID для каждого результата
                title=item.get('name'),
                input_message_content=InputTextMessageContent(  # ОБЯЗАТЕЛЬНО!
                    message_text=(
                        f"<code>{item.get('name')}</code>\n"
                    ),
                    parse_mode='HTML',
                    disable_web_page_preview=True
                ),
            )
        )
    
    await inline_query.answer(
        results=inline_results,
        cache_time=1,  # Кэшировать на 1 секунду
        is_personal=True  # Результаты персональные
    )


@router.inline_query()
async def inline_search(inline_query: InlineQuery):
    """
    Обрабатывает инлайн-запросы: выводит все названия игр
    Вызывается когда пользователь вводит @username_бота текст
    """
    
    query = inline_query.query.strip()
    
    if not query:
        # Если запрос пустой, показываем подсказку
        await inline_query.answer(
            results=[],
            switch_pm_text="Начните вводить текст для поиска",
            switch_pm_parameter="start",
            cache_time=300
        )
        return
    
    # Поиск в БД по запросу
    results = await db.fetch(f"SELECT name from games_list where name ILIKE $1 ORDER BY name", f'%{query}%')
    
    # Преобразуем результаты в формат для Telegram
    inline_results = []
    
    for i, item in enumerate(results[:50]):  # Telegram ограничивает 50 результатов
        inline_results.append(
            InlineQueryResultArticle(
                id=str(i),  # ОБЯЗАТЕЛЬНО! Уникальный ID для каждого результата
                title=item.get('name'),
                input_message_content=InputTextMessageContent(  # ОБЯЗАТЕЛЬНО!
                    message_text=(
                        f"<code>{item.get('name')}</code>\n"
                    ),
                    parse_mode='HTML',
                    disable_web_page_preview=True
                ),
            )
        )
    
    await inline_query.answer(
        results=inline_results,
        cache_time=1,  # Кэшировать на 1 секунду
        is_personal=True  # Результаты персональные
    )
    
    
