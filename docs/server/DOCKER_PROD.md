# Обновление кода и поднятие стека (прод)

Раздел для `docs/server/`. Описывает полный цикл: забрал новый код → пересобрал → поднял → проверил. Плюс разбор ситуаций, когда что-то пошло не так.

## Базовые правила

- Сервер работает **только из `main`**. На сервере не коммитим и не правим файлы: любое изменение едет через PR на GitHub.
- `.env` не отслеживается git: `git pull` и `reset --hard` его не трогают.
- Данные живут в named volumes (`postgres_data`, `redis_data`, `beat_data`). Они переживают пересоздание контейнеров. Удаляются только командой `docker compose down -v` — **на проде она запрещена**.
- Все compose-команды на сервере выполняются с `-f docker-compose.prod.yaml`: дефолтный `docker-compose.yaml` — это конфигурация локальной разработки.

## Штатная процедура обновления

```bash
cd /opt/erp

# 1. Убедиться, что сервер чистый и стоит на main
git status                          # ожидаем: working tree clean

# 2. Подтянуть новый код
git fetch origin
git pull --ff-only origin main

# 3. Пересобрать образы (обязательно, если менялись requirements.txt или Dockerfile)
docker compose -f docker-compose.prod.yaml build

# 4. Поднять стек
docker compose -f docker-compose.prod.yaml up -d

# 5. Проверить
docker compose -f docker-compose.prod.yaml ps                      # все сервисы Up
docker compose -f docker-compose.prod.yaml logs migrate --tail=20  # миграции применились
docker compose -f docker-compose.prod.yaml logs --tail=30 bot      # бот стартовал
docker compose -f docker-compose.prod.yaml logs --tail=30 worker   # воркер поднялся
```

Что происходит на шаге 4: compose сравнивает запущенные контейнеры с конфигурацией; если образ или конфиг изменились — останавливает старый контейнер, удаляет его и создаёт новый из нового образа. Named volumes не удаляются, данные БД и Redis сохраняются. Даунтайм — несколько секунд.

Проверка, что новый код доехал до контейнера:

```bash
docker compose -f docker-compose.prod.yaml exec bot ls /app/src/app/core/service/labels/
```

> Если стек на проде управляется systemd, шаг 4 заменяется на `sudo systemctl restart erp`, статус — `sudo systemctl status erp`.

## Если pull не тянет изменения (сервер разошёлся с GitHub)

Симптомы: `git pull --ff-only` падает с ошибкой, `git status` пишет ahead/behind, новые файлы не появляются.

Диагностика:

```bash
git fetch origin
git log --oneline origin/main..main   # локальные коммиты, которых нет на GitHub
git log --oneline main..origin/main   # коммиты, которые ещё не подтянуты
```

Если первая команда непустая — на сервере кто-то коммитил напрямую. Если эти коммиты не нужны:

```bash
# Страховка локальных коммитов (создаёт указатель, ничего не удаляет)
git branch backup/server-main-$(date +%Y%m%d-%H%M%S)

# Страховка незакоммиченных правок отслеживаемых файлов (без -u, чтобы не утащить .env)
git stash push -m "server-dirty-before-reset"

# Если отслеживаемые файлы правились руками (например compose) — копия вне репозитория
cp docker-compose.yaml /root/docker-compose.server-backup.yaml

# ВНИМАНИЕ: перезаписывает рабочую папку содержимым origin/main
git reset --hard origin/main

git status                            # ожидаем: working tree clean
```

Дальше — штатная процедура с шага 3. Бэкап-ветку и stash удалять через несколько дней стабильной работы.

Если локальные коммиты нужны — reset не делать: перенести их в PR с рабочей машины.

## Если файлы на диске есть, а приложение их не видит

1. Проверить диск: `ls src/app/core/service/labels/`
2. Проверить, что образ пересобран: `docker compose -f docker-compose.prod.yaml images` (колонка CREATED). Старая дата — `build` не выполнялся.
3. Пересоздать контейнеры: `docker compose -f docker-compose.prod.yaml up -d`. Без этого запущенные контейнеры продолжают жить в старом образе.
4. Проверить внутри контейнера: `docker compose -f docker-compose.prod.yaml exec bot ls /app/src/app/core/service/labels/`

## Откат на предыдущую версию

```bash
cd /opt/erp
git fetch origin --tags
git checkout v2.1.0                   # detached HEAD для отката — нормально
docker compose -f docker-compose.prod.yaml build
docker compose -f docker-compose.prod.yaml up -d
```

Возврат на актуальную версию: `git switch main && git pull --ff-only origin main`, затем шаги 3–4 штатной процедуры.

## Шпаргалка

| Хочу | Команда |
|---|---|
| Подтянуть новый код | `git pull --ff-only origin main` |
| Пересобрать образы | `docker compose -f docker-compose.prod.yaml build` |
| Поднять / обновить стек | `docker compose -f docker-compose.prod.yaml up -d` |
| Кто работает | `docker compose -f docker-compose.prod.yaml ps` |
| Логи бота | `docker compose -f docker-compose.prod.yaml logs -f bot` |
| Логи миграций | `docker compose -f docker-compose.prod.yaml logs migrate` |
| Файлы внутри контейнера | `docker compose -f docker-compose.prod.yaml exec bot ls /app/src` |
| Пересоздать контейнеры принудительно | `docker compose -f docker-compose.prod.yaml up -d --force-recreate` |
| Остановить стек | `docker compose -f docker-compose.prod.yaml down` (без `-v`!) |