from fastapi import FastAPI, Request, Response
from app.api.routers import router
from app.models.database import database, engine, Base
import logging
import json
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(router)

@app.on_event("startup")
async def startup():
    await database.connect()
    logger.info("Подключение к базе данных установлено")

    try:
        db = SessionLocal()
        
        from app.models.database import WarehouseState, Movement
        
        warehouse_state = db.query(WarehouseState).filter(
            WarehouseState.warehouse_id == "c1d70455-7e14-11e9-812a-70106f431230"
        ).first()
        
        if not warehouse_state:
            warehouse_data = WarehouseState(
                id="c1d70455-7e14-11e9-812a-70106f431230:4705204f-498f-4f96-b4ba-df17fb56bf55",
                warehouse_id="c1d70455-7e14-11e9-812a-70106f431230",
                product_id="4705204f-498f-4f96-b4ba-df17fb56bf55",
                quantity=100
            )
            db.add(warehouse_data)
            logger.info(f"Добавлены тестовые данные о состоянии склада: {warehouse_data}")
            
            departure_time = datetime.now() - timedelta(hours=2)
            arrival_time = datetime.now() - timedelta(hours=1)
            
            movement_data = Movement(
                movement_id="c6290746-790e-43fa-8270-014dc90e02e0",
                source_warehouse="WH-3322",
                destination_warehouse="WH-3423",
                product_id="4705204f-498f-4f96-b4ba-df17fb56bf55",
                departure_time=departure_time,
                arrival_time=arrival_time,
                time_difference_seconds=3600.0,
                departure_quantity=100,
                arrival_quantity=100,
                quantity_difference=0
            )
            db.add(movement_data)
            db.commit()
            logger.info(f"Добавлены тестовые данные о перемещении: {movement_data}")
        
        db.close()
    except Exception as e:
        logger.error(f"Ошибка при добавлении тестовых данных: {e}")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    logger.info("Соединение с базой данных закрыто")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)