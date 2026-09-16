🏠 ГЛАВНАЯ · main
│
├── 📁 📦 ТОВАРЫ · main-goods
│   │
│   ├── ⚡ [ 🔻 ПОКУПКА · buy | 🔼 ПРОДАЖА · sell ]
│   ├── ⚡ ✅ ЗАКАЗ ПОЛУЧЕН · order_arrived
│   ├── ⚡ [ 🔄 ОБМЕН · swap | 🎫 БРОНЬ · reserve ]
│   ├── ⚡ 💵 ОБНОВИТЬ ЦЕНУ ПРОДАЖИ · change_selling_price
│   ├── ⚡ ➕ ДОБАВИТЬ ТРАНЗАКЦИЮ · add_trns
│   │
│   ├── 📁 🚚 СКЛАД И ДОСТАВКА · main-goods-warehouse_delivery
│   │   ├── ⚡ [ 🚚 КО МНЕ · delivery_to_me | 🚚 К КЛИЕНТАМ · delivery_to_client ]
│   │   └── ⚡ 💿 НАЛИЧИЕ · available
│   │
│   └── 📁 🛠️ УПРАВЛЕНИЕ ЗАПИСЯМИ · main-goods-records_management
│       ├── ⚡ 🔧 ИЗМЕНИТЬ ПО ID · change_row_by_id
│       └── ⚡ ❌ УДАЛИТЬ ПО ID · delete_row_by_id
│
├── 📁 📦 ОПТОВЫЕ ЗАКАЗЫ · main-bulk_orders
│   │
│   ├── ⚡ 🆕 СОЗДАТЬ · new_bulk_order
│   ├── ⚡ 🚚 ДОБАВИТЬ ДОСТАВКУ · add_delivery_to_bulk_order
│   ├── ⚡ ✅ ПРИЕХАЛ · bulk_order_arrived
│   │
│   ├── 📁 👁️ ПРОСМОТР ЗАКАЗОВ · main-bulk_orders-view_orders
│   │   ├── ⚡ 🚚 ЕДУТ КО МНЕ · bulk_orders_come_to_me
│   │   └── ⚡ [ 📦 ПО ID · bulk_order_by_id | 🗃️ ВСЕ · all_bulk_orders ]
│   │
│   └── 📁 🛠️ УПРАВЛЕНИЕ · main-bulk_orders-management
│       └── ⚡ ❌ УДАЛИТЬ ЗАКАЗ · delete_bulk_order
│
├── 📁 🛒 МАРКЕТПЛЕЙСЫ · main-marketplaces
│   ├── 📁 🟠 АВИТО · main-marketplaces-avito
│   └── 📁 🔵 ОЗОН · main-marketplaces-ozon
│
└── 📁 ⚙️ ДОПОЛНИТЕЛЬНО · main-extra
    │
    ├── 📁 📊 ОТЧЁТЫ · main-extra-reports
    │   ├── ⚡ 📊 ПОЛНЫЙ ФИНАНСОВЫЙ ОТЧЁТ · full_finance_report
    │   └── ⚡ 📈 ОТЧЁТ ПО ТОВАРАМ ЗА ПЕРИОД · product_report_period
    │
    ├── 📁 🎮 КАТАЛОГ ИГР · main-extra-games_catalog
    │   ├── ⚡ 🆕 ДОБАВИТЬ ИГРУ · add_game
    │   └── ⚡ ❌ УДАЛИТЬ ИГРУ · delete_game
    │
    └── 📁 📝 ОПИСАНИЕ ОБЪЯВЛЕНИЙ · main-extra-description
        ├── ⚡ 👁️ ПОСМОТРЕТЬ ОПИСАНИЕ · view_description
        └── ⚡ 🏷️ ИЗМЕНИТЬ ТЕГИ · change_personal_tags