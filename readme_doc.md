# Документация проекта Bristol_test: Сервис мониторинга состояния складов

## Описание

Этот проект представляет собой микросервис на Python с использованием FastAPI, предназначенный для обработки сообщений от складов через Kafka. Сообщения уведомляют о приемках и отправках товаров. Сервис сохраняет данные о перемещениях и предоставляет API для получения информации о конкретных перемещениях и текущих состояниях складов.

База данных SQLite используется для хранения информации о состоянии складов и движениях товаров. Kafka выступает в роли брокера сообщений для асинхронной обработки событий со складов.

## Структура проекта

-   `app/`: Основная директория с кодом приложения.
    -   `main.py`: Точка входа FastAPI приложения, инициализация, обработчики событий startup/shutdown (включая запуск Kafka-консьюмера и подключение к БД).
    -   `api/`: Модули, связанные с API.
        -   `routers.py`: Определения API эндпоинтов.
    -   `core/`: Основные конфигурационные файлы.
        -   `config.py`: Загрузка настроек приложения (например, из переменных окружения).
    -   `models/`: Модели данных и схемы.
        -   `database.py`: Настройка подключения к базе данных (SQLAlchemy, `databases`).
        -   `schemas.py`: Pydantic-схемы для валидации данных и сериализации.
    -   `services/`: Бизнес-логика и сервисы.
        -   `kafka_consumer.py`: Логика Kafka-консьюмера.
        -   `warehouse_service.py`: Логика обработки сообщений и взаимодействия с БД.
-   `tests/`: Директория для тестов (пока пустая).
-   `Dockerfile`: Инструкции для сборки Docker-образа приложения.
-   `pyproject.toml`: Файл для управления зависимостями с помощью Poetry.
-   `readme_doc.md`: Этот файл документации.
-   `README.md`: Оригинальный файл README с описанием задания.
-   `.gitignore`: Файл для исключения ненужных файлов из Git.

## Предварительные требования

1.  **Docker**: Установленный и запущенный Docker Desktop или Docker Engine.
2.  **Poetry (опционально, для локальной разработки)**: Если вы планируете работать с зависимостями или запускать проект локально без Docker, установите Poetry ([инструкция](https://python-poetry.org/docs/#installation)).

## Переменные окружения

Приложение использует следующие переменные окружения. Вы можете создать файл `.env` в корне проекта или передать их при запуске Docker-контейнера:

-   `APP_NAME`: Название приложения (по умолчанию: "Сервис мониторинга состояния складов").
-   `KAFKA_BOOTSTRAP_SERVERS`: Адрес и порт Kafka-брокера. 
    -   Пример для Docker Compose, если сервис Kafka называется `kafka`: `kafka:29092`.
    -   Пример для локально запущенной Kafka: `localhost:9092`.
-   `KAFKA_TOPIC`: Название Kafka-топика для чтения сообщений (по умолчанию: `ru.retail.warehouses`).
-   `DATABASE_URL`: URL для подключения к базе данных. 
    -   Для SQLite внутри контейнера (файл будет создан в рабочей директории `/app`): `sqlite:///./warehouse.db`.

**Пример `.env` файла:**

```env
APP_NAME="Сервис Склада"
KAFKA_BOOTSTRAP_SERVERS="kafka:29092"
KAFKA_TOPIC="ru.retail.warehouses"
DATABASE_URL="sqlite:///./warehouse.db"
```

## Установка и запуск (с Docker)

**Рекомендуемый способ: использование Docker Compose (см. следующий раздел).**

Если вы все же хотите использовать отдельные команды `docker build` и `docker run`:

1.  **Сборка Docker-образа:**

    Откройте терминал в корневой директории проекта и выполните:

    ```bash
    docker build -t bristol-test-service .
    ```

2.  **Запуск Docker-контейнера:**

    Для запуска потребуется работающий экземпляр Kafka. Если вы используете Docker Compose для запуска Kafka, убедитесь, что имя сервиса Kafka и порт соответствуют значению `KAFKA_BOOTSTRAP_SERVERS`.

    **Примечание:** Если контейнер с таким именем (`bristol-app` в примере ниже) уже существует, команда `docker run` завершится ошибкой. В этом случае вам нужно сначала остановить и удалить существующий контейнер:
    ```bash
    docker stop bristol-app
    docker rm bristol-app
    ```

    Пример запуска контейнера с передачей переменных окружения:

    ```bash
    docker run -d -p 8000:8000 \
      -e KAFKA_BOOTSTRAP_SERVERS="ваш_kafka_хост:порт" \
      -e KAFKA_TOPIC="ru.retail.warehouses" \
      -e DATABASE_URL="sqlite:///./warehouse.db" \
      --name bristol-app \
      bristol-test-service
    ```

3.  **Доступ к приложению:**

    После запуска контейнера API будет доступно по адресу `http://localhost:8000`.
    OpenAPI документация (Swagger UI) будет доступна по адресу `http://localhost:8000/docs`.

## Запуск с Docker Compose (Рекомендуется)

Для удобного управления всеми сервисами (ваше приложение, Kafka, Zookeeper) рекомендуется использовать Docker Compose.

1.  **Создайте файл `docker-compose.yml`** в корне проекта (если вы этого еще не сделали). Актуальную версию файла можно найти в истории чата или сгенерировать заново, если потребуется.

2.  **(Опционально) Создайте файл `.env`** в корне проекта для переменных окружения, если вы предпочитаете их хранить отдельно от `docker-compose.yml`.

3.  **Запустите все сервисы:**
    В корневой директории проекта выполните:
    ```bash
    docker-compose up --build -d
    ```
    Эта команда соберет образ вашего приложения (если он изменился или еще не собран) и запустит все сервисы в фоновом режиме. Docker Compose автоматически обработает существующие контейнеры (пересоздаст их при необходимости).

4.  **Доступ к приложению:**

    После запуска API будет доступно по адресу `http://localhost:8000`.
    OpenAPI документация (Swagger UI) будет доступна по адресу `http://localhost:8000/docs`.

5.  **Просмотр логов:**
    ```bash
    docker-compose logs app  # Для логов вашего приложения
    docker-compose logs kafka # Для логов Kafka
    # и т.д.
    ```

6.  **Остановка сервисов:**
    ```bash
    docker-compose down
    ```

## Локальная разработка (без Docker, с Poetry)

1.  **Установка зависимостей:**

    Убедитесь, что у вас установлен Poetry. В корне проекта выполните:

    ```bash
    poetry install
    ```
    Эта команда создаст виртуальное окружение (если его нет) и установит все зависимости из `pyproject.toml`.
    Если файл `poetry.lock` отсутствует, он будет создан. Рекомендуется добавить `poetry.lock` в систему контроля версий.

2.  **Активация виртуального окружения Poetry:**

    ```bash
    poetry shell
    ```

3.  **Настройка переменных окружения:**

    Создайте файл `.env` в корне проекта с необходимыми переменными (см. раздел "Переменные окружения"). Убедитесь, что `KAFKA_BOOTSTRAP_SERVERS` указывает на ваш локальный Kafka.

4.  **Запуск приложения:**

    Для запуска FastAPI приложения с Uvicorn:

    ```bash
    uvicorn app.main:app --reload
    ```
    Флаг `--reload` включает автоматическую перезагрузку при изменениях в коде.

## API Эндпоинты

Префикс для всех API: `/api`

### 1. Получение информации о перемещении

-   **URL:** `/api/movements/{movement_id}`
-   **Метод:** `GET`
-   **Описание:** Возвращает информацию о перемещении по его ID, включая отправителя, получателя, время, прошедшее между отправкой и приемкой, и разницу в количестве товара.
-   **Пример ответа (успех):**
    ```json
    {
      "movement_id": "c6290746-790e-43fa-8270-014dc90e02e0",
      "source_warehouse": "WH-3322",
      "destination_warehouse": "WH-3423",
      "product_id": "4705204f-498f-4f96-b4ba-df17fb56bf55",
      "departure_time": "2025-02-18T12:12:56Z",
      "arrival_time": "2025-02-18T14:34:56Z",
      "time_difference_seconds": 8520.0,
      "departure_quantity": 100,
      "arrival_quantity": 100,
      "quantity_difference": 0
    }
    ```
-   **Пример ответа (ошибка - не найдено):**
    ```json
    {
      "detail": "Перемещение не найдено"
    }
    ```

### 2. Получение информации о состоянии склада

-   **URL:** `/api/warehouses/{warehouse_id}/products/{product_id}`
-   **Метод:** `GET`
-   **Описание:** Возвращает информацию о текущем запасе товара в конкретном складе.
-   **Пример ответа (успех):**
    ```json
    {
      "warehouse_id": "c1d70455-7e14-11e9-812a-70106f431230",
      "product_id": "4705204f-498f-4f96-b4ba-df17fb56bf55",
      "quantity": 150
    }
    ```

### Корневой эндпоинт

-   **URL:** `/`
-   **Метод:** `GET`
-   **Описание:** Возвращает приветственное сообщение.
-   **Пример ответа:**
    ```json
    {
      "message": "Добро пожаловать в Сервис мониторинга состояния складов"
    }
    ```

## Запуск Kafka (пример)

Для работы сервиса необходим запущенный Kafka. Если у вас нет настроенного Kafka, вы можете быстро запустить его локально с помощью Docker Compose. Создайте файл `docker-compose.yml` (если вы не используете его для всего проекта) со следующим содержимым:

```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.3.0
    container_name: zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.3.0
    container_name: kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092" # Для доступа с хост-машины (если KAFKA_BOOTSTRAP_SERVERS="localhost:9092")
      # - "29092:29092" # Для доступа из других Docker контейнеров в той же сети (KAFKA_BOOTSTRAP_SERVERS="kafka:29092")
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_CONFLUENT_LICENSE_TOPIC_REPLICATION_FACTOR: 1 # Confluent specific
      KAFKA_CONFLUENT_BALANCER_TOPIC_REPLICATION_FACTOR: 1 # Confluent specific
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1             # Confluent specific
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1  # Confluent specific
```

Запустите Kafka командой `docker-compose up -d` в директории с этим файлом.
Убедитесь, что топик `ru.retail.warehouses` создан в Kafka, или что Kafka настроена на автоматическое создание топиков.

---
*(Эта документация была сгенерирована и дополнена AI-ассистентом)* 