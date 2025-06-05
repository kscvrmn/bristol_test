from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, MetaData, Table, ForeignKey, UniqueConstraint
from datetime import datetime
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
metadata = MetaData()

warehouse_states = Table(
    "warehouse_states",
    metadata,
    Column("id", String, primary_key=True),
    Column("warehouse_id", String, index=True),
    Column("product_id", String, index=True),
    Column("quantity", Integer, default=0),
    UniqueConstraint("warehouse_id", "product_id", name="uix_warehouse_product")
)

movements = Table(
    "movements",
    metadata,
    Column("movement_id", String, primary_key=True),
    Column("source_warehouse", String, nullable=True),
    Column("destination_warehouse", String, nullable=True),
    Column("product_id", String, index=True),
    Column("departure_time", DateTime, nullable=True),
    Column("arrival_time", DateTime, nullable=True),
    Column("time_difference_seconds", Float, nullable=True),
    Column("departure_quantity", Integer, nullable=True),
    Column("arrival_quantity", Integer, nullable=True),
    Column("quantity_difference", Integer, nullable=True),
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

metadata.create_all(engine)

from databases import Database
database = Database(DATABASE_URL)