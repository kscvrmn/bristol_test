FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей для psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Копирование только файлов зависимостей для кэширования слоев
COPY pyproject.toml poetry.lock* ./

# Добавление psycopg2-binary и asyncpg в зависимости
RUN pip install --no-cache-dir psycopg2-binary asyncpg alembic

# Настройка Poetry для установки зависимостей в системный Python
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# Копирование скрипта запуска
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Копирование остальных файлов проекта
COPY . .

# Экспозиция порта
EXPOSE 8000

# Запуск приложения
CMD ["/app/start.sh"] 