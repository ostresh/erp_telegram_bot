Локальная инструкция — коротко и по делу.

---

## Два режима работы

| Режим | Файл | Файл окружения | Где |
|---|---|---|---|
| **Локальный** (разработка) | `docker-compose.yaml` | `.env.docker` | локальная машина |
| **Прод** (сервер) | `docker-compose.prod.yaml` | `.env` | сервер `/opt/erp` |

---

## Сервисы и их роль

| Сервис | Что делает |
|---|---|
| `postgres` | База данных (только в проде; локально подключается внешняя) |
| `redis` | Кэш и брокер очередей для Celery |
| `bot` | Telegram-бот, точка входа для пользователей |
| `worker` | Фоновые задачи (отчёты, выгрузки) |
| `beat` | Планировщик, запускает задачи по расписанию |
| `migrate` | Миграции БД (прод, одноразово при старте) |

---

## Локальный запуск

```bash
cd <папка_проекта>

# поднять всё
docker compose up -d --build

# смотреть логи
docker compose logs -f bot
docker compose logs -f worker

# остановить
docker compose down
```

Контейнеры локально имеют суффикс `-local` (`erp-bot-local` и т.д.).

---

## Прод (сервер)

На проде управляет `systemd`, вручную `docker compose` обычно не дёргают.

```bash
# статус стека
sudo systemctl status erp

# перезапуск
sudo systemctl restart erp

# остановить / запустить
sudo systemctl stop erp
sudo systemctl start erp

# фактическое состояние контейнеров
cd /opt/erp && sudo docker compose -f docker-compose.prod.yaml ps
```

---

## Логи

```bash
# локально — лог конкретного сервиса
docker compose logs -f <сервис>

# прод — через docker
cd /opt/erp && sudo docker compose -f docker-compose.prod.yaml logs --tail=100 bot

# прод — лог самого стека (systemd)
journalctl -u erp -n 100 --no-pager
```

---

## Бэкапы (прод)

```bash
# когда следующий бэкап
systemctl list-timers backup-erp.timer

# запустить бэкап сейчас
sudo systemctl start backup-erp.service

# проверить актуальность бэкапов
/usr/local/bin/check-erp-backups.sh

# список бэкапов
ls -lah /opt/erp/backups/daily/
```

---

## Частые операции

**Деплой новой версии (прод):**
```bash
cd /opt/erp
git pull
sudo docker compose -f docker-compose.prod.yaml build
sudo systemctl restart erp
sudo docker compose -f docker-compose.prod.yaml ps
```

**Применить миграции вручную (локально):**
```bash
docker compose run --rm bot python -m manage migrate upgrade
```

**Проверить здоровье БД (прод):**
```bash
cd /opt/erp && sudo docker compose -f docker-compose.prod.yaml exec postgres pg_isready
```

**Место на диске:**
```bash
df -h
docker system df
```

---

## Быстрая шпаргалка

| Хочу... | Команда |
|---|---|
| Поднять локально | `docker compose up -d --build` |
| Перезапустить прод | `sudo systemctl restart erp` |
| Видеть, что работает | `docker compose ps` |
| Смотреть логи | `docker compose logs -f bot` |
| Запустить бэкап | `sudo systemctl start backup-erp.service` |
| Обновить прод | `git pull` → `build` → `systemctl restart erp` |