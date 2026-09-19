"""
Хендлер: Поиск игр через inline-запросы.

Используется когда пользователь вводит @имя_бота текст в чате.
Показывает список игр, соответствующих запросу.
"""

from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from app.db.unit_of_work import UnitOfWork
from app.service import GameService, RecordService
import logging

logger = logging.getLogger(__name__)
router = Router(name="search")


@router.inline_query(F.query.startswith("@to_me "))
async def search_delivery_to_me_games(inline_query: InlineQuery, uow: UnitOfWork):
    """
    Обрабатывает инлайн-запросы: выводит игры по названию, которые едут ко мне.
    
    Вызывается когда пользователь вводит @имя_бота текст.
    
    Пример:
        @MyBot @to_me witcher → найдёт все игры с "witcher" в названии из наличия
    """
    
    query = inline_query.query.replace('@to_me ', '').strip()
    
    # Если запрос пустой, показываем подсказку
    if not query:
        await inline_query.answer(
            results=[],
            switch_pm_text="Начните вводить текст для поиска",
            switch_pm_parameter="start",
            cache_time=300,
        )
        return
    
    async with uow() as session:
        service = GameService(session)
        games = await service.search_delivery_to_me(query)
    
        
    if not games:
        await inline_query.answer(
            results=[],
            switch_pm_text="Игры не найдены",
            switch_pm_parameter="start",
            cache_time=1,
        )
        return
    
    # Преобразуем результаты в формат для Telegram
    inline_results = []
    
    for i, game in enumerate(games):
        inline_results.append(
            InlineQueryResultArticle(
                id=str(i),
                title=game.name,
                input_message_content=InputTextMessageContent(
                    message_text=f"<code>{game.name}</code>",
                    parse_mode="HTML",
                ),
            )
        )
    
    await inline_query.answer(
        results=inline_results,
        cache_time=1,
        is_personal=True,
    )
    
    logger.info(
        f"User {inline_query.from_user.id} searched for '{query}', "
        f"found {len(games)} results"
    )

@router.inline_query(F.query.startswith("@to_client "))
async def search_delivery_to_client_games(inline_query: InlineQuery, uow: UnitOfWork):
    """
    Обрабатывает инлайн-запросы: выводит игры по названию, которые едут к покупателю.
    
    Вызывается когда пользователь вводит @имя_бота текст.
    
    Пример:
        @MyBot @to_client witcher → найдёт все игры с "witcher" в названии из наличия
    """
    
    query = inline_query.query.replace('@to_client ', '').strip()
    
    # Если запрос пустой, показываем подсказку
    if not query:
        await inline_query.answer(
            results=[],
            switch_pm_text="Начните вводить текст для поиска",
            switch_pm_parameter="start",
            cache_time=300,
        )
        return
    
    async with uow() as session:
        service = GameService(session)
        games = await service.search_delivery_to_client(query)
    
        
    if not games:
        await inline_query.answer(
            results=[],
            switch_pm_text="Игры не найдены",
            switch_pm_parameter="start",
            cache_time=1,
        )
        return
    
    # Преобразуем результаты в формат для Telegram
    inline_results = []
    
    for i, game in enumerate(games):
        inline_results.append(
            InlineQueryResultArticle(
                id=str(i),
                title=game.name,
                input_message_content=InputTextMessageContent(
                    message_text=f"<code>{game.name}</code>",
                    parse_mode="HTML",
                ),
            )
        )
    
    await inline_query.answer(
        results=inline_results,
        cache_time=1,
        is_personal=True,
    )
    
    logger.info(
        f"User {inline_query.from_user.id} searched for '{query}', "
        f"found {len(games)} results"
    )

@router.inline_query(F.query.startswith("@available "))
async def search_available_games(inline_query: InlineQuery, uow: UnitOfWork):
    """
    Обрабатывает инлайн-запросы: выводит игры по названию.
    
    Вызывается когда пользователь вводит @имя_бота текст.
    
    Пример:
        @MyBot @available witcher → найдёт все игры с "witcher" в названии из наличия
    """
    
    query = inline_query.query.replace('@available ', '').strip()
    
    # Если запрос пустой, показываем подсказку
    if not query:
        await inline_query.answer(
            results=[],
            switch_pm_text="Начните вводить текст для поиска",
            switch_pm_parameter="start",
            cache_time=300,
        )
        return
    
    async with uow() as session:
        service = GameService(session)
        games = await service.search_available(query)
    
        
    if not games:
        await inline_query.answer(
            results=[],
            switch_pm_text="Игры не найдены",
            switch_pm_parameter="start",
            cache_time=1,
        )
        return
    
    # Преобразуем результаты в формат для Telegram
    inline_results = []
    
    for i, game in enumerate(games):
        inline_results.append(
            InlineQueryResultArticle(
                id=str(i),
                title=game.name,
                input_message_content=InputTextMessageContent(
                    message_text=f"<code>{game.name}</code>",
                    parse_mode="HTML",
                ),
            )
        )
    
    await inline_query.answer(
        results=inline_results,
        cache_time=1,
        is_personal=True,
    )
    
    logger.info(
        f"User {inline_query.from_user.id} searched for '{query}', "
        f"found {len(games)} results"
    )
    

@router.inline_query()
async def search_games(inline_query: InlineQuery, uow: UnitOfWork):
    """
    Обрабатывает инлайн-запросы: выводит игры по названию.
    
    Вызывается когда пользователь вводит @имя_бота текст.
    
    Пример:
        @MyBot witcher → найдёт все игры с "witcher" в названии
    """
    
    query = inline_query.query.strip()
    
    # Если запрос пустой, показываем подсказку
    if not query:
        await inline_query.answer(
            results=[],
            switch_pm_text="Начните вводить текст для поиска",
            switch_pm_parameter="start",
            cache_time=300,
        )
        return
    
    async with uow() as session:
        service = GameService(session)
        games = await service.search(query)
    
        
    if not games:
        await inline_query.answer(
            results=[],
            switch_pm_text="Игры не найдены",
            switch_pm_parameter="start",
            cache_time=1,
        )
        return
    
    # Преобразуем результаты в формат для Telegram
    inline_results = []
    
    for i, game in enumerate(games):
        inline_results.append(
            InlineQueryResultArticle(
                id=str(i),
                title=game.name,
                input_message_content=InputTextMessageContent(
                    message_text=f"<code>{game.name}</code>",
                    parse_mode="HTML",
                ),
            )
        )
    
    await inline_query.answer(
        results=inline_results,
        cache_time=1,
        is_personal=True,
    )
    
    logger.info(
        f"User {inline_query.from_user.id} searched for '{query}', "
        f"found {len(games)} results"
    )