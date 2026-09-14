

class ActionLabel:
    """
    Названия действий для кнопок и сообщений.

    Используются в хендлерах для отображения действий пользователя.
    """

    
    # Записи
    BUY = "🔻 ПОКУПКА"
    SELL = "🔼 ПРОДАЖА"
    ARRIVED = "✅ ЗАКАЗ ПОЛУЧЕН"
    SWAP = "🔄 ОБМЕН"
    RESERVE = "🎫 БРОНЬ"
    
    # Оптовые заказы
    NEW_BULK_ORDER = "🆕 СОЗДАТЬ ЗАКАЗ"
    ADD_DELIVERY_BULK_ORDER = "🚚💰 ДОБАВИТЬ ДОСТАВКУ"
    BULK_ORDER_ARRIVED = "✅ ЗАКАЗ ПРИЕХАЛ"
    DELETE_BULK_ORDER_BY_ID = "❌ УДАЛИТЬ ЗАКАЗ ПО ID"
    
    # Уведомления
    GENERAL_NOTICE = "🔹 ОБЩЕЕ"
    PERSONAL_NOTICE = "🔑 ЧАСТНОЕ"
    FOR_NEW_NOTICE = "🆕 ДЛЯ НОВЫХ"
    FOR_USED_NOTICE = "♻️ ДЛЯ Б/У"
    CHANGE_PERSONAL_TAG = "🔧 ИЗМЕНИТЬ ЧАСТНЫЙ ТЭГ"
    CHANGE_BASE_FOR_NOTICE = "🔧 ИЗМЕНИТЬ БАЗУ"
    HEADER_NOTICE = "🎩📋 ШАПКА ДЛЯ ОПИСАНИЯ"
    BASE_TAGS_NOTICE = "📝 БАЗОВЫЕ ТЕГИ"
    BASE_PERSONAL = "🔑 БАЗА ЧАСТНОГО ОПИСАНИЯ"
    
    # Сервис
    CHANGE_ROW_BY_ID = "🔧 ИЗМЕНИТЬ СТРОКУ ПО ID"
    DELETE_ROW_BY_ID = "❌ УДАЛИТЬ СТРОКУ ПО ID"
    UPDATE_PRICE_FOR_SPECIFIC_GAMES = "🛠️ УСТАНОВИТЬ ОДНУ ЦЕНУ ИГРАМ"
    ADD_GAME_IN_GAMES_LIST = "🆕 ДОБАВИТЬ ИГРУ В СПИСОК"
    DELETE_GAME_FROM_GAMES_LIST = "❌ УДАЛИТЬ ИГРУ ИЗ СПИСКА"
    
    # Доставка
    LOCAL = "📍 ЛОКАЛЬНО"
    DELIVERY = "🚚 С ДОСТАВКОЙ"
    
    # Финансы
    ALL_FINANCES = "📊 ВСЕ ФИНАНСЫ"
    
    # Транзакции
    ADD_TRNS = '📝 Добавить транзакцию'
    
    # Третий уровень: main-info-records
    COME_TO_ME = "🚚👤 КО МНЕ"
    COME_TO_CLIENT = "🚚👥 К КЛИЕНТАМ"
    INTERVAL = "🔢 ЗАПИСИ ПО ИНТЕРВАЛУ"
    
    # Третий уровень: main-info-bulk_order
    BULK_ORDER_BY_ID = "📦 ЗАКАЗ ПО ID"
    ALL_BULK_ORDERS = "🗃️ ВСЕ ОПТОВЫЕ ЗАКАЗЫ"
    
    # Третий уровень: main-info-available
    AVAILABLE_FOR_ME = "🔒 ДЛЯ МЕНЯ"
    AVAILABLE_FOR_CLIENT = "👥 ДЛЯ КЛИЕНТА"
    AVAILABLE_BY_RECORDS = "🆔 НАЛИЧИЕ ПО ЗАПИСЯМ"