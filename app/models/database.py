from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import databases
from app.core.config import settings

# SQLAlchemy
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


database = databases.Database(DATABASE_URL)

metadata = MetaData()

warehouse_states = Table(
    "warehouse_states",
    metadata,
    Column("id", String, primary_key=True),
    Column("warehouse_id", String, index=True),
    Column("product_id", String, index=True),
    Column("quantity", Integer),
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

class WarehouseState(Base):
    __tablename__ = "warehouse_states"
    
    id = Column(String, primary_key=True)
    warehouse_id = Column(String, index=True)
    product_id = Column(String, index=True)
    quantity = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<WarehouseState(warehouse_id='{self.warehouse_id}', product_id='{self.product_id}', quantity={self.quantity})>"

class Movement(Base):
    __tablename__ = "movements"
    
    movement_id = Column(String, primary_key=True)
    source_warehouse = Column(String, nullable=True)
    destination_warehouse = Column(String, nullable=True)
    product_id = Column(String, index=True)
    departure_time = Column(DateTime, nullable=True)
    arrival_time = Column(DateTime, nullable=True)
    time_difference_seconds = Column(Float, nullable=True)
    departure_quantity = Column(Integer, nullable=True)
    arrival_quantity = Column(Integer, nullable=True)
    quantity_difference = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<Movement(movement_id='{self.movement_id}', product_id='{self.product_id}')>"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()