FROM python:3.9-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir psycopg2-binary asyncpg alembic

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

COPY . .

# Экспозиция порта
EXPOSE 8000

# Запуск приложения
CMD ["/app/start.sh"] 