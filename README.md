# ERP Telegram Bot

Telegram-бот для учёта продаж и движения товара (игровые диски): закупки, продажи,
оптовые заказы, склад/доставка, финансовые показатели и Excel-отчёты.
Бот работает в режиме личного кабинета: доступ есть только у владельца (`OWNER_ID`).

## Возможности

- **Товары**: покупка, продажа, получение заказа, изменение цены продажи,
  добавление транзакции (площадки покупки/продажи).
- **Дополнительно по товарам**: обмен, бронь, комментарий, склад и доставка
  («в пути ко мне» / «в пути к клиенту»), наличие по записям и по играм,
  управление записями (отмена заказа, редактирование, удаление).
- **Оптовые заказы**: создание, добавление доставки, отметка прибытия,
  просмотр активных и всех заказов, удаление.
- **Отчёты**: отчёт по движению товаров, отчёт по продажам, полный финансовый отчёт.
  Excel-выгрузки формируются в фоне (Celery) и отправляются в чат.
- **Справочники**: каталог игр (добавление, изменение, удаление),
  описание объявления (просмотр, изменение).
- **Динамическое меню**: дерево меню в коде, хлебные крошки, навигация inline-кнопками,
  финансовая сводка в главном меню.
- **Автоочистка чата**: сервисные сообщения бота удаляются планировщиком (Celery beat).
- **Развёртывание**: Docker Compose для локального запуска и для продакшена.

## Требования

- Python **3.14** (базовый образ `python:3.14-slim`; локально проверено на 3.14.7).
- **PostgreSQL** (драйвер `asyncpg`; в проде используется `postgres:17`).
- **Redis 7** — брокер и backend для Celery.
- **Docker** и **Docker Compose v2** — для контейнерного запуска.
- Токен Telegram-бота (получается у [@BotFather](https://t.me/BotFather))
  и Telegram ID владельца.
- Доступ к Telegram API (в режиме `development` допускается SOCKS5-прокси).

## Установка

### Вариант 1. Локально (Python + venv)

```bash
git clone https://github.com/ostresh/erp_telegram_bot.git
cd erp_telegram_bot

python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

Создайте файл окружения и заполните его:

```bash
cp .env.example .env
```

Затем примените миграции (из каталога `src`, где лежит `manage.py`):

```bash
cd src
python -m manage migrate upgrade
```

### Вариант 2. Docker Compose (локально)

```bash
cp .env.example .env.docker
# заполните .env.docker
docker compose up -d --build
```

Локальный `docker-compose.yaml` поднимает `redis`, `bot`, `worker`, `beat`.
PostgreSQL в него не входит — используется внешняя БД. Если БД запущена на хосте,
укажите `DB_HOST=host.docker.internal`.

### Вариант 3. Docker Compose (прод)

```bash
cp .env.example .env
# заполните .env
docker compose -f docker-compose.prod.yaml up -d --build
```

Прод-конфигурация поднимает `postgres`, `redis`, одноразовый сервис миграций
`migrate`, `bot`, `worker` и `beat`. Подробности эксплуатации — в
`docs/server/DEVELOPMENT.md` и `docs/server/SERVER.md`.

## Быстрый старт

Минимальный путь до рабочего бота (Docker):

```bash
cp .env.example .env.docker
```

Заполните минимум: `BOT_TOKEN`, `OWNER_ID`, `DB_HOST`, `DB_PORT`, `DB_NAME`,
`DB_USER`, `DB_PASSWORD`, `INITIAL_BALANCE`, `REVENUE`, `DISCS_COUNT_SOLD`,
`ALL_ASSETS`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `ENVIRONMENT`.

```bash
docker compose up -d --build
docker compose run --rm bot python -m manage migrate upgrade
docker compose logs -f bot
```

Откройте бота в Telegram и отправьте `/start` — откроется главное меню.

> Схема БД: текущая миграция в репозитории пустая (см. раздел «TODO»),
> поэтому таблицы нужно создать отдельно — новой миграцией или дампом.

Пример значений для локального Redis в Docker:

```dotenv
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
ENVIRONMENT=development
```

## Использование

Управление проектом выполняется через CLI `manage.py` (запуск из каталога `src`):

```bash
python -m manage                 # справка
python -m manage run bot         # Telegram-бот (polling)
python -m manage run celery worker
python -m manage run celery beat
python -m manage run celery all  # worker + beat в одном процессе
```

Миграции (Alembic):

```bash
python -m manage migrate init "Add email to records"  # autogenerate
python -m manage migrate upgrade                      # по умолчанию head
python -m manage migrate downgrade -1
python -m manage migrate current
python -m manage migrate history
python -m manage migrate check
python -m manage migrate sql
```

Прямой запуск Celery (используется в docker-compose):

```bash
python -m celery -A app.core.tasks.celery_app worker --loglevel=info
python -m celery -A app.core.tasks.celery_app beat --loglevel=info
```

Сценарий работы в боте:

1. `/start` — главное меню (единственная команда бота).
2. Навигация по разделам — inline-кнопки: «Товары», «Оптовые заказы»,
   «Маркетплейсы», «Дополнительно».
3. Отчёты: «Дополнительно» → «Отчёты» → выбор отчёта и периода.
   Задача ставится в очередь Celery, готовый `.xlsx` приходит в чат.
4. Сервисные сообщения бота удаляются автоматически (задача
   `cleanup_expired_messages` запускается каждый час).

Структура меню описана в `docs/architecture/menu/menu_tree.md`.

## Конфигурация

Переменные читаются из `.env` (`src/config.py`, `python-dotenv`).
Файл `.env.example` — шаблон.

| Переменная | Обязательна | Назначение |
|---|---|---|
| `BOT_TOKEN` | да | Токен Telegram-бота. Без него бот завершает работу с ошибкой в логе. |
| `OWNER_ID` | да | Telegram ID единственного пользователя, которому разрешён доступ (по умолчанию `0` — доступ никому). |
| `ENVIRONMENT` | да | `development` или `production`. В `development` бот создаёт сессию с прокси, в `production` — без. |
| `PROXY_URL` | нет | SOCKS5-прокси для режима `development` (используется только там). |
| `DB_HOST` | да | Хост PostgreSQL. |
| `DB_PORT` | да | Порт PostgreSQL (приводится к `int`). |
| `DB_NAME` | да | Имя базы данных. |
| `DB_USER` | да | Пользователь БД. |
| `DB_PASSWORD` | да | Пароль БД. |
| `INITIAL_BALANCE` | да | Начальный баланс, учитывается в финансовом отчёте. |
| `REVENUE` | да | Поправка к выручке в финансовом отчёте. |
| `DISCS_COUNT_SOLD` | да | Поправка к количеству проданных дисков. |
| `ALL_ASSETS` | да | Поправка к сумме активов. |
| `CELERY_BROKER_URL` | да* | Брокер Celery (например, `redis://redis:6379/0`). |
| `CELERY_RESULT_BACKEND` | да* | Backend результатов Celery. |

\* Без этих переменных не запустятся `worker` и `beat`; сам бот стартует,
но фоновые задачи (отчёты, очистка) работать не будут.

Особенности:

- Числовые переменные (`DB_PORT`, `INITIAL_BALANCE`, `REVENUE`, `DISCS_COUNT_SOLD`,
  `ALL_ASSETS`) преобразуются через `int()` при импорте конфига — пустые значения
  приводят к ошибке запуска.
- `ENVIRONMENT` вызывается через `.lower()`, поэтому переменная должна быть задана.
- Часовой пояс Celery — `Europe/Moscow`.

## Тестирование

Автоматических тестов в репозитории нет: отсутствуют каталог `tests`,
зависимость `pytest` и конфигурация тестового запуска.

Команда `python -m manage test` тестами не является — она запускает
локальный скрипт `src/playground/main.py`. Каталог `src/playground` исключён
из git и из Docker-образа, поэтому в свежем клоне команда завершится ошибкой
(модуль отсутствует). Скрипт служит песочницей для ручных запросов к сервисам
и требует рабочей БД.

Проверка вручную:

```bash
python -m manage run bot    # бот запускается, в логе "Database connection successful"
```

## Структура проекта

```
Bot/
├── Dockerfile                  # образ приложения (python:3.14-slim)
├── docker-compose.yaml         # локально: redis, bot, worker, beat
├── docker-compose.prod.yaml    # прод: postgres, redis, migrate, bot, worker, beat
├── requirements.txt            # зафиксированные зависимости
├── .env.example                # шаблон переменных окружения
├── docs/
│   ├── architecture/menu/      # дерево меню
│   ├── notes/                  # рабочие заметки (в .gitignore)
│   └── server/                 # эксплуатация: сервер, деплой, бэкапы
└── src/
    ├── manage.py               # CLI: run, migrate, test
    ├── config.py               # чтение переменных окружения
    ├── app/
    │   ├── core/
    │   │   ├── db/             # модели SQLAlchemy, репозитории, UnitOfWork, Alembic
    │   │   ├── dto/            # DTO и финансовые модели
    │   │   ├── service/        # бизнес-логика: товары, заказы, меню, отчёты, Excel
    │   │   ├── tasks/          # Celery: celery_app, очистка сообщений, отчёты
    │   │   └── utils/          # логирование (colorlog)
    │   ├── integrations/       # интеграции (gtable — пустая заглушка)
    │   └── interfaces/bot/     # aiogram: main, handlers, dialogs, middlewares, callbacks
    └── playground/             # локальные скрипты (в .gitignore)
```

Архитектура слоёв:

- `interfaces/bot` — Telegram-слой (aiogram 3 + aiogram-dialog): роутеры,
  диалоги, middleware авторизации и `UnitOfWork`.
- `core/service` — бизнес-логика, не зависит от Telegram.
- `core/db/repository` — доступ к данным; транзакциями управляет `UnitOfWork`
  (коммит при успехе, откат при исключении).
- `core/db/models.py` — модели: `Game`, `Utility`, `Description`, `Record`,
  `BulkOrder`, `MessageToDelete`.
- `core/tasks` — фоновые задачи Celery; в worker используется `CeleryUnitOfWork`
  с `NullPool`.

## Разработка

1. Создайте ветку и внесите изменения.
2. Соблюдайте слоистость: обработчики и диалоги вызывают сервисы, сервисы —
   репозитории; SQL в слое интерфейсов не пишется.
3. Новый диалог: каталог в `src/app/interfaces/bot/dialogs/actions/` с файлами
   `dialog.py`, `states.py`, `getter.py`, `flow.py`, `event_handler.py`;
   регистрация — в `ACTION_DIALOGS`.
4. Новый пункт меню: узел в `src/app/core/service/menu/tree.py` и подписи
   в `src/app/interfaces/bot/messages/menu/`.
5. Изменение схемы БД: правка `core/db/models.py` →
   `python -m manage migrate init "..."` → проверка файла миграции →
   `python -m manage migrate upgrade`.
6. Запуск стека локально: `docker compose up -d --build`,
   логи: `docker compose logs -f bot`.
7. Обновите документацию в `docs/`, если меняется поведение или эксплуатация.

Полезные материалы:

- `docs/notes/handlers/aiogram-dialog.md` — шпаргалка по aiogram-dialog 2.6.0.
- `docs/server/DEVELOPMENT.md` — локальный запуск, прод, логи, бэкапы.
- `docs/server/SERVER.md` — описание инфраструктуры и регламента обслуживания.

CI/CD в репозитории не настроен (каталог `.github` отсутствует), линтеры
и форматтеры не зафиксированы в зависимостях.

## TODO и открытые вопросы

- **Миграция пустая**: `src/app/core/db/alembic/versions/20261019_1333_new_db.py`
  содержит `pass` в `upgrade()`/`downgrade()`, поэтому `migrate upgrade` не создаёт
  таблицы. Нужна актуальная миграция (или дамп схемы) — иначе БД придётся
  готовить вручную.
- **Расхождение имён переменных**: `.env.example` содержит `HTTP_PROXY` и
  `HTTPS_PROXY`, а код читает `PROXY_URL`. Требуется привести шаблон и код
  к одному имени.
- **`.env.docker` отсутствует в репозитории** (игнорируется git), но требуется
  локальному `docker-compose.yaml`. Нужно описать/автоматизировать его создание.
- **`./db_dumps` отсутствует**: прод-конфигурация монтирует каталог в
  `/docker-entrypoint-initdb.d`. Источник дампа для инициализации БД не описан.
- **Раздел «Маркетплейсы»** (Авито, Озон) в меню — заглушки без обработчиков;
  `src/app/integrations/gtable/` пуст. Интеграции не реализованы.
- **Тесты**: нет автотестов и тестовой инфраструктуры (pytest, фикстуры, БД
  для тестов). `manage test` запускает playground.
- **Лицензия** не указана — файл `LICENSE` отсутствует.
- **Версия Python 3.14** зафиксирована только в `Dockerfile`; в README/CI
  она не закреплена (нет `.python-version`, `pyproject.toml`).

## Лицензия

Данные о лицензии в репозитории отсутствуют.
