"""
Названия действий для кнопок и сообщений.

Используются в хендлерах для отображения действий пользователя.
"""


class ActionLabel:
    """Названия действий"""
    
    # Товары
    BUY = "🔻 ПОКУПКА"
    SELL = "🔼 ПРОДАЖА"
    ORDER_ARRIVED = "✅ ПОЛУЧЕНИЕ ЗАКАЗА"
    SWAP = "🔄 ОБМЕН"
    RESERVE = "🎫 БРОНЬ"
    CHANGE_SELLING_PRICE = "💵 ИЗМЕНИТЬ ЦЕНУ ПРОДАЖИ"
    ADD_TRNS = "➕ ДОБАВИТЬ ТРАНЗАКЦИЮ"
    COMMENT = "💬 ДОБАВИТЬ КОММЕНТАРИЙ"
    
    # Склад и доставка
    IN_TRANSIT_TO_ME = "🚚 КО МНЕ"
    IN_TRANSIT_TO_CLIENT = "🚚 К КЛИЕНТАМ"
    AVAILABLE = "💿 НАЛИЧИЕ НА СКЛАДЕ"
    
    # Управление записями
    CHANGE_ROW_BY_ID = "🔧 РЕДАКТИРОВАТЬ ЗАПИСЬ"
    DELETE_ROW_BY_ID = "❌ УДАЛИТЬ ЗАПИСЬ"
    
    # Оптовые заказы
    NEW_BULK_ORDER = "🆕 СОЗДАТЬ ОПТОВЫЙ ЗАКАЗ"
    ADD_DELIVERY_TO_BULK_ORDER = "🚚 ДОБАВИТЬ ДОСТАВКУ К ЗАКАЗУ"
    BULK_ORDER_ARRIVED = "✅ ОТМЕТИТЬ ПРИБЫТИЕ ЗАКАЗА"
    BULK_ORDERS_COME_TO_ME = "🚚 В ПУТИ КО МНЕ"
    BULK_ORDER_BY_ID = "📦 ПОИСК ПО ID"
    ALL_BULK_ORDERS = "🗃️ ВСЕ ЗАКАЗЫ"
    DELETE_BULK_ORDER = "❌ УДАЛИТЬ ЗАКАЗ"
    
    # Отчёты
    FULL_FINANCE_REPORT = "📊 ПОЛНЫЙ ФИНАНСОВЫЙ ОТЧЁТ"
    PRODUCT_REPORT_PERIOD = "📊 ТОВАРНЫЙ ОТЧЕТ ЗА ПЕРИОД"
    
    # Каталог игр
    ADD_GAME = "🆕 ДОБАВИТЬ ИГРУ"
    DELETE_GAME = "❌ УДАЛИТЬ ИГРУ"
    
    # Описание объявления
    VIEW_DESCRIPTION = "📝 ПРОСМОТРЕТЬ ОПИСАНИЕ"
    CHANGE_PERSONAL_TAGS = "🔧 ИЗМЕНИТЬ ОПИСАНИЕ ОБЪЯВЛЕНИЯ"