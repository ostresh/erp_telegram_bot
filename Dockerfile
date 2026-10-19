# Актуальная версия Python (октябрь 2026)
FROM python:3.14-slim

# Встроенные переменные окружения (не секреты!)
# PYTHONDONTWRITEBYTECODE=1 - не создавать .pyc файлы
# PYTHONUNBUFFERED=1 - не буферизировать stdout (важно для логов)
# PIP_NO_CACHE_DIR=1 - не кэшировать пакеты pip
# PYTHONPATH=/app/src - Python ищет модули в /app/src
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src

# Системные зависимости для компиляции C-расширений (asyncpg)
RUN apt-get update && apt-get install -y \
    gcc \
    libc-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Контейнерное приложение не должно работать под root
RUN groupadd --system app \
    && useradd --system \
        --gid app \
        --create-home \
        --home-dir /home/app \
        app

WORKDIR /app

RUN chown app:app /app

# Копируем requirements.txt отдельно для кэширования
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY --chown=app:app . .

USER app

# Запуск по умолчанию (переопределим в docker-compose для каждого сервиса)
CMD ["python", "-m", "manage", "run", "bot"]