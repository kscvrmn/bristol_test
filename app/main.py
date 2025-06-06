from fastapi import FastAPI, Request, Response
from app.api.routers import router
from app.models.database import database, engine, Base, warehouse_states, movements
import logging
import json
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
        query = warehouse_states.select().where(
            warehouse_states.c.warehouse_id == "c1d70455-7e14-11e9-812a-70106f431230"
        )
        warehouse_state = await database.fetch_one(query)
        
        if not warehouse_state:
            """Добавление тестовых данных"""
            warehouse_id = "c1d70455-7e14-11e9-812a-70106f431230"
            product_id = "4705204f-498f-4f96-b4ba-df17fb56bf55"

            warehouse_state_id = f"{warehouse_id}:{product_id}"
            query = warehouse_states.insert().values(
                id=warehouse_state_id,
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity=100
            )
            await database.execute(query)
            
            query = warehouse_states.select().where(warehouse_states.c.id == warehouse_state_id)
            warehouse_state = await database.fetch_one(query)
            logger.info(f"Добавлены тестовые данные о состоянии склада: {warehouse_state}")
            
            now = datetime.utcnow()
            movement_id = "c6290746-790e-43fa-8270-014dc90e02e0"
            query = movements.insert().values(
                movement_id=movement_id,
                source_warehouse="WH-3322",
                destination_warehouse="WH-3423",
                product_id=product_id,
                departure_time=now - timedelta(hours=1),
                arrival_time=now,
                time_difference_seconds=3600.0,
                departure_quantity=100,
                arrival_quantity=100,
                quantity_difference=0
            )
            await database.execute(query)
            
            query = movements.select().where(movements.c.movement_id == movement_id)
            movement = await database.fetch_one(query)
            logger.info(f"Добавлены тестовые данные о перемещении: {movement}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении тестовых данных: {str(e)}")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    logger.info("Соединение с базой данных закрыто")