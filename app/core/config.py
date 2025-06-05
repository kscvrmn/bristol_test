from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    APP_NAME: str = "Сервис мониторинга состояния складов"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/warehouse")
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC: str = os.getenv("KAFKA_TOPIC", "warehouse_events")
    KAFKA_GROUP_ID: str = os.getenv("KAFKA_GROUP_ID", "warehouse_consumer")

    class Config:
        env_file = ".env"


settings = Settings()