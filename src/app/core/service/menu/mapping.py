"""
Справочники (маппинги) для UI.

Единая точка, где живут id и title всех выборов меню:
получатель, доставка и т.д.
"""


class RecipientMapping:
    """Получатель заказа."""

    TO_ME = 'to_me'
    TO_CLIENT = 'to_client'

    METHODS = [
        {'id': TO_ME, 'title': '🚚 КО МНЕ'},
        {'id': TO_CLIENT, 'title': '🚚 К КЛИЕНТАМ'},
    ]

    TITLES = {method['id']: method['title'] for method in METHODS}


class DeliveryMapping:
    """Способ доставки."""

    LOCAL = 'local'
    DELIVERY = 'delivery'

    METHODS = [
        {'id': LOCAL, 'title': '📍 ЛОКАЛЬНО'},
        {'id': DELIVERY, 'title': '🚚 С ДОСТАВКОЙ'},
    ]

    TITLES = {method['id']: method['title'] for method in METHODS}